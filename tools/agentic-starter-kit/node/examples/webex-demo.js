import { WebexClient } from "../src/webexClient.js";

const client = new WebexClient();

const spaces = await client.listSpaces();
console.log(`Spaces found: ${spaces.length}`);
for (const space of spaces.slice(0, 5)) {
  console.log("-", space.title || space.id);
}

if (spaces.length > 0) {
  // Use the first available space to keep the starter flow short.
  const messages = await client.listMessages(spaces[0].id);
  console.log(`Messages in first space: ${messages.length}`);
  for (const message of messages.slice(0, 5)) {
    console.log("-", (message.text || "").trim().slice(0, 80) || "<no text>");
  }
}

try {
  const recordings = await client.listRecordings();
  console.log(`Recordings found: ${recordings.length}`);
} catch (error) {
  console.log("Recording list failed:", error.message);
  console.log("This can happen if the PAT owner does not have meeting recording access.");
}

try {
  const transcripts = await client.listTranscripts();
  console.log(`Transcripts found: ${transcripts.length}`);
  if (transcripts.length > 0) {
    const details = await client.getTranscriptDetails(transcripts[0].id);
    console.log("First transcript id:", details.id);
  }
} catch (error) {
  // Transcript access is often empty or restricted even when spaces work.
  console.log("Transcript access failed:", error.message);
  console.log("This can happen if the PAT owner does not have transcript access or none are available.");
}
