import http from "k6/http";
import { check } from "k6";

export const options = {
  vus: 500,
  duration: "30s",
};

export default function () {
  const res = http.get("http://localhost:5000/urls/1");
  check(res, { "status is 200": (r) => r.status === 200 });
  if (res.status !== 200) {
    console.log(`Failed: ${res.status} ${res.body}`);
  }
}
