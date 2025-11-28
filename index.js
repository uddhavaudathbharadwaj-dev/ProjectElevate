import express from "express";
import fetch from "node-fetch";
import cors from "cors";

const app = express();

app.use(cors());
app.use(express.json());

// Health check
app.get("/", (req, res) => {
  res.send("✅ Project Elevate chat backend is awake.");
});

// Chat endpoint for frontend
app.post("/chat", async (req, res) => {
  const { message } = req.body; // matches frontend { message: userInput }

  if (!message) return res.status(400).json({ error: "No message provided" });

  try {
    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort(), 15000); // 15s timeout

    const response = await fetch("https://openrouter.ai/api/v1/chat/completions", {
      method: "POST",
      headers: {
        "Authorization": Bearer ${process.env.OPENROUTER_API_KEY},
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        model: "kwaipilot/kat-coder-pro:free",
        messages: [
          {
            role: "system",
            content: `
You are an AI tutor called Project Elevate. Answer politely, concisely, and clearly.
Do not return HTML—just plain text messages.
Be friendly, supportive, and educational.
`
          },
          { role: "user", content: message },
        ],
      }),
      signal: controller.signal,
    });

    clearTimeout(timeout);

    const data = await response.json();

    const aiMessage = data?.choices?.[0]?.message?.content || "AI didn't respond.";
    res.json({ response: aiMessage });

  } catch (err) {
    console.error("❌ Error:", err.message);
    res.status(500).json({ error: "Internal Server Error", details: err.message });
  }
});

// Avoid favicon errors
app.get(["/favicon.ico", "/favicon.png"], (req, res) => res.status(204).end());

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => console.log(🚀 Chat backend running on port ${PORT}));

export default app;
