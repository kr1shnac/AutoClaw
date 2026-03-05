// vercel_queue/api/telegram_webhook.js
// Receives POST requests from Telegram and stores commands in a queue file.
// This runs as a serverless function on Vercel's free tier.

import { promises as fs } from 'fs';
import path from 'path';

// Vercel's /tmp directory is the only writable area in serverless functions
const QUEUE_FILE = path.join('/tmp', 'command_queue.json');

export default async function handler(req, res) {
    if (req.method !== 'POST') {
        return res.status(405).json({ error: 'Method Not Allowed' });
    }

    try {
        const body = req.body;
        const message = body?.message;

        if (!message || !message.text) {
            // Acknowledge receipt even if no useful message (e.g., edit events)
            return res.status(200).json({ ok: true });
        }

        const command = {
            chat_id: message.chat.id,
            user_id: message.from.id,
            username: message.from.username || 'unknown',
            text: message.text,
            received_at: new Date().toISOString(),
        };

        // Read existing queue or start fresh
        let queue = [];
        try {
            const data = await fs.readFile(QUEUE_FILE, 'utf8');
            queue = JSON.parse(data);
        } catch {
            // File doesn't exist yet — start fresh
            queue = [];
        }

        queue.push(command);
        await fs.writeFile(QUEUE_FILE, JSON.stringify(queue, null, 2));

        console.log(`Queued command from @${command.username}: ${command.text}`);
        return res.status(200).json({ ok: true });

    } catch (error) {
        console.error('Webhook error:', error);
        return res.status(500).json({ error: 'Internal Server Error' });
    }
}
