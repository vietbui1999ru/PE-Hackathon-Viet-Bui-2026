import http from "k6/http";
import { check } from "k6";

// Fail on CI no Green Checks
export const options = {
  vus: 500,
  duration: "15s",
  thresholds: {
    http_req_failed: ["rate<0.05"], // fail if error rate > 5%
    http_req_duration: ["p(95)<3000"], // fail if p95 > 3s
  },
};

// LOCAL TEST
// export default function () {
//   const res = http.get("http://localhost:5000/urls/1");
//   check(res, { "status is 200": (r) => r.status === 200 });
//   if (res.status !== 200) {
//     console.log(`Failed: ${res.status} ${res.body}`);
//   }
// }

// CI TEST
export default function () {
  const res = http.get("http://localhost:5000/urls/1");
  check(res, { "status is 200": (r) => r.status === 200 });
}
