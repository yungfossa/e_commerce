import logging

from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor


class SpanFormatter(logging.Formatter):
    """
    Custom log formatter that includes trace ID in log records.

    This formatter extends the standard logging.Formatter to include
    the current span's trace ID in each log record. This is useful for
    correlating logs with distributed traces.
    """

    def format(self, record):
        """
        Format the specified record as text.

        Args:
            record (logging.LogRecord): The log record to format.

        Returns:
            str: The formatted log record.
        """
        trace_id = trace.get_current_span().get_span_context().trace_id
        if trace_id == 0:
            record.trace_id = None
        else:
            record.trace_id = "{trace:032x}".format(trace=trace_id)
        return super().format(record)


def build_instrumentation(hostname: str, port: int):
    """
    Set up OpenTelemetry instrumentation for the application.

    This function configures OpenTelemetry to export traces to a
    specified endpoint using the OTLP (OpenTelemetry Protocol) exporter.

    Args:
        hostname (str): The hostname of the OpenTelemetry collector.
        port (int): The port number of the OpenTelemetry collector.
    """
    resource = Resource(attributes={"service.name": "ss-backend"})

    trace.set_tracer_provider(TracerProvider(resource=resource))
    otlp_exporter = OTLPSpanExporter(endpoint=f"{hostname}:{port}", insecure=True)
    trace.get_tracer_provider().add_span_processor(BatchSpanProcessor(otlp_exporter))


# This module sets up OpenTelemetry instrumentation for the application.
# OpenTelemetry is an observability framework for cloud-native software.

# Key components:
# 1. SpanFormatter: A custom log formatter that includes trace IDs in log records.
#    This helps in correlating logs with distributed traces.

# 2. build_instrumentation: A function to set up the OpenTelemetry trace provider
#    and exporter. It configures the application to send traces to a specified
#    OpenTelemetry collector.

# Usage:
# The build_instrumentation function should be called during application startup,
# typically in the app factory or main initialization code.

# Example:
#   build_instrumentation("localhost", 4317)

# Note: This setup assumes the use of an OpenTelemetry collector at the specified
# hostname and port. Ensure that the collector is properly configured and running
# to receive and process the traces.

# Security Note:
# The current setup uses an insecure connection to the OpenTelemetry collector.
# For production environments, consider using a secure connection.
