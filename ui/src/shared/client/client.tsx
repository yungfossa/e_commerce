export default class Client {
	access_token: string;

	constructor(access_token: string) {
		this.access_token = access_token;
	}

	async get(url: string): Promise<any> {
		return fetch(url, {
			headers: {
				Authorization: `Bearer ${this.access_token}`,
			},
		})
			.then((r) => r.json())
			.catch((e) => {
				throw e;
			});
	}

	async post(url: string, body: any): Promise<any> {
		return fetch(url, {
			method: "POST",
			headers: {
				Authorization: `Bearer ${this.access_token}`,
				"Content-Type": "application/json",
			},
			body: JSON.stringify(body),
		})
			.then((r) => r.json())
			.catch((e) => {
				throw e;
			});
	}
}
