import json


def send_json_response(self, status_code, response):

        response_body = json.dumps(
            response
        ).encode("utf-8")

        self.send_response(status_code)

        self.send_header(
            "Content-Type",
            "application/json"
        )

        self.send_header(
            "Content-Length",
            str(len(response_body))
        )

        self.end_headers()
        try:
            self.wfile.write(response_body)
            self.wfile.flush()
            
        except ConnectionAbortedError:
            print("Client closed the connection before receiving the response.")