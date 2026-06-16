import { request } from "./client";

export function getProfile() {
  return request("/profile/me");
}

export function updateProfile(profileData) {
  return request("/profile/me", {
    method: "PUT",
    body: JSON.stringify(profileData),
  });
}

// Daily macro targets for the saved profile (no side effects).
export function getNeeds() {
  return request("/profile/needs");
}
