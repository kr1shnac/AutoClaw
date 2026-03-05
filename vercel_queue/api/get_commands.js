// vercel_queue/api/get_commands.js
// GET endpoint that the local Python poller fetches to retrieve waiting commands.
// Automatically clears the queue after returning (one-time read).

import { promises as fs } from 'fs';
import path from 'path';

const QUEUE_FILE = path.join('/tmp', 'command_queue.json');

export default async function handler(req, res) {
    if (req.method !== 'GET') {
        return res.status(405).json({ error: 'Method Not Allowed' });
    }

    try {
        let queue = [];
        try {
            const data = await fs.readFile(QUEUE_FILE, 'utf8');
            queue = JSON.parse(data);
        } catch {
            // No queue yet — return empty
            queue = [];
        }

        // Clear the queue after returning (one-time read)
        await fs.writeFile(QUEUE_FILE, JSON.stringify([], null, 2));

        return res.status(200).json({ commands: queue });

    } catch (error) {
        console.error('Get commands error:', error);
        return res.status(500).json({ error: 'Internal Server Error' });
    }
}
