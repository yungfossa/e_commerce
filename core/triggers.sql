-- Function to handle the purchase of items from a customer's cart
CREATE OR REPLACE FUNCTION purchase_items(customer_id INT)
RETURNS VOID AS $$
DECLARE
    item_id INT;
BEGIN
    -- Iterate through items in the cart for the given customer
    FOR item_id IN
        SELECT cart.item_id
        FROM cart
        JOIN listings ON cart.item_id = listings.id
        WHERE cart.customer_id = customer_id
        FOR UPDATE SKIP LOCKED  -- Lock the listing rows to prevent concurrent updates
    LOOP
        -- Attempt to decrease the availability of the listing by one
        UPDATE listings
        SET available_quantity = available_quantity - 1
        WHERE id = item_id
        AND available_quantity > 0; -- Ensure it's still available
        -- Check if the update was successful
        IF NOT FOUND THEN
            RAISE NOTICE 'Item % is no longer available for purchase', item_id;
        ELSE
            -- Empty the cart for this customer
            DELETE FROM cart WHERE customer_id = customer_id;
        END IF;
    END LOOP;
    -- Commit the transaction
    COMMIT;
EXCEPTION
    WHEN OTHERS THEN
        -- Rollback in case of any error
        ROLLBACK;
        RAISE;
END;
$$ LANGUAGE plpgsql;

-- Function to prevent invalid order status transitions
CREATE OR REPLACE FUNCTION prevent_invalid_order_status_transition()
RETURNS TRIGGER AS $$
BEGIN
    -- Prevent changing order status to 'pending' from any other state
    IF NEW.order_status = 'pending' AND OLD.order_status != 'pending' THEN
        RAISE EXCEPTION 'Cannot change order status to PENDING from the current state.'
            USING ERRCODE = 'invalid_parameter_value';
    END IF;

    -- Prevent changing order status to 'cancelled' after it has been 'delivered'
    IF NEW.order_status = 'cancelled' AND OLD.order_status = 'delivered' THEN
        RAISE EXCEPTION 'Cannot change order status to CANCELLED after being DELIVERED.'
            USING ERRCODE = 'invalid_parameter_value';
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger to execute the prevent_invalid_order_status_transition function
CREATE TRIGGER prevent_invalid_order_status_transition
BEFORE UPDATE ON orders
FOR EACH ROW
EXECUTE FUNCTION prevent_invalid_order_status_transition();

-- Function to ensure a seller can only have one listing per product
CREATE OR REPLACE FUNCTION check_unique_product_listing_per_seller()
RETURNS TRIGGER AS $$
DECLARE
    existing_count INT;
BEGIN
    -- Check if a listing for this product by this seller already exists
    SELECT COUNT(*)
    INTO existing_count
    FROM listings
    WHERE product_id = NEW.product_id AND seller_id = NEW.seller_id;

    IF existing_count > 0 THEN
        RAISE EXCEPTION 'A listing for this product by this seller already exists.'
            USING ERRCODE = 'unique_violation';
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger to execute the check_unique_product_listing_per_seller function
CREATE TRIGGER unique_product_listing_per_seller
BEFORE INSERT ON listings
FOR EACH ROW
EXECUTE FUNCTION check_unique_product_listing_per_seller();

-- Function to update product state when a listing is updated
CREATE OR REPLACE FUNCTION update_product_state_on_listing_update()
RETURNS TRIGGER AS $$
BEGIN
    -- If the listing is marked as unavailable, check if it's the last available listing
    IF NEW.is_available = FALSE THEN
        UPDATE products
        SET product_state = CASE
            WHEN (SELECT COUNT(*) FROM listings WHERE product_id = NEW.product_id AND is_available = TRUE) = 0 THEN 'used'
            ELSE product_state
        END
        WHERE id = NEW.product_id;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger to execute the update_product_state_on_listing_update function
CREATE TRIGGER update_product_state_on_listing_update
AFTER UPDATE ON listings
FOR EACH ROW
EXECUTE FUNCTION update_product_state_on_listing_update();

-- Function to update word occurrences when a product is inserted
CREATE OR REPLACE FUNCTION update_word_occurrences_on_product_insert()
RETURNS TRIGGER AS $$
DECLARE
    words_list TEXT;
    word TEXT;
BEGIN
    -- Combine name and description
    words_list := NEW.name || ' ' || NEW.description;

    -- Loop through each word and insert into words and word_occurrences
    WHILE LENGTH(words_list) > 0 LOOP
        word := SPLIT_PART(words_list, ' ', 1);
        words_list := SUBSTRING(words_list FROM LENGTH(word) + 2);

        -- Insert or update word and get its ID
        WITH inserted_word AS (
            INSERT INTO words (word)
            VALUES (word)
            ON CONFLICT (word) DO UPDATE SET word = EXCLUDED.word
            RETURNING id
        )
        -- Insert word occurrence
        INSERT INTO word_occurrences (word_id, product_id)
        SELECT id, NEW.id FROM inserted_word;
    END LOOP;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger to execute the update_word_occurrences_on_product_insert function
CREATE TRIGGER update_word_occurrences_on_product_insert
AFTER INSERT ON products
FOR EACH ROW
EXECUTE FUNCTION update_word_occurrences_on_product_insert();

-- Function to update word occurrences when a product is updated
CREATE OR REPLACE FUNCTION update_word_occurrences_on_product_update()
RETURNS TRIGGER AS $$
DECLARE
    words_list TEXT;
    word TEXT;
BEGIN
    -- Delete existing occurrences for this product
    DELETE FROM word_occurrences WHERE product_id = OLD.id;

    -- Repeat the insertion logic from the previous trigger
    words_list := NEW.name || ' ' || NEW.description;

    WHILE LENGTH(words_list) > 0 LOOP
        word := SPLIT_PART(words_list, ' ', 1);
        words_list := SUBSTRING(words_list FROM LENGTH(word) + 2);

        WITH inserted_word AS (
            INSERT INTO words (word)
            VALUES (word)
            ON CONFLICT (word) DO UPDATE SET word = EXCLUDED.word
            RETURNING id
        )
        INSERT INTO word_occurrences (word_id, product_id)
        SELECT id, NEW.id FROM inserted_word;
    END LOOP;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger to execute the update_word_occurrences_on_product_update function
CREATE TRIGGER update_word_occurrences_on_product_update
AFTER UPDATE ON products
FOR EACH ROW
EXECUTE FUNCTION update_word_occurrences_on_product_update();

-- Function to delete word occurrences when a product is deleted
CREATE OR REPLACE FUNCTION delete_word_occurrences_on_product_delete()
RETURNS TRIGGER AS $$
BEGIN
    -- Remove all word occurrences associated with the deleted product
    DELETE FROM word_occurrences WHERE product_id = OLD.id;
    RETURN OLD;
END;
$$ LANGUAGE plpgsql;

-- Trigger to execute the delete_word_occurrences_on_product_delete function
CREATE TRIGGER delete_word_occurrences_on_product_delete
AFTER DELETE ON products
FOR EACH ROW
EXECUTE FUNCTION delete_word_occurrences_on_product_delete();
