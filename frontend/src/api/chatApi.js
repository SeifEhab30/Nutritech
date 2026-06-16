import { getToken } from "./authApi";

const BASE_URL = "http://127.0.0.1:8000";

export async function askChatbot(message, history = []) {
  const token = getToken();
  const res = await fetch(`${BASE_URL}/chat/ask`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
    },
    body: JSON.stringify({ message, history }),
  });

  if (!res.ok) {
    const text = await res.text();
    throw new Error(text || "Server error");
  }

  const data = await res.json();
  return data.reply;
}