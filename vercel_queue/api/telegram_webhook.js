// vercel_queue/api/telegram_webhook.js (Updated for Task 3.2)
// Adds server-side ID whitelist check before queuing any command.

import { promises as fs } from 'fs';
import path from 'path';

const QUEUE_FILE = path.join('/tmp', 'command_queue.json');

function getAuthorizedIds() {
    const raw = process.env.AUTHORIZED_TELEGRAM_IDS || '';
    return new Set(raw.split(',').map(id => parseInt(id.trim(), 10)).filter(Boolean));
}

export default async function handler(req, res) {
    if (req.method !== 'POST') {
        return res.status(405).json({ error: 'Method Not Allowed' });
    }

    try {
        const body = req.body;
        const message = body?.message;

        if (!message || !message.text) {
            return res.status(200).json({ ok: true });
        }

        const userId = message.from?.id;

        // ── Security Gate ──────────────────────────────────────
        const authorizedIds = getAuthorizedIds();
        if (!authorizedIds.has(userId)) {
            // Silently drop — never reveal the bot to unauthorized users
            console.log(`[SECURITY] Dropped message from unauthorized user_id=${userId}`);
            return res.status(200).json({ ok: true });
        }
        // ───────────────────────────────────────────────────────

        const command = {
            chat_id: message.chat.id,
            user_id: userId,
            username: message.from.username || 'unknown',
            text: message.text,
            received_at: new Date().toISOString(),
        };

        let queue = [];
        try {
            const data = await fs.readFile(QUEUE_FILE, 'utf8');
            queue = JSON.parse(data);
        } catch {
            queue = [];
        }

        queue.push(command);
        await fs.writeFile(QUEUE_FILE, JSON.stringify(queue, null, 2));

        console.log(`[QUEUE] Queued command from @${command.username}: ${command.text}`);
        return res.status(200).json({ ok: true });

    } catch (error) {
        console.error('Webhook error:', error);
        return res.status(500).json({ error: 'Internal Server Error' });
    }
}
