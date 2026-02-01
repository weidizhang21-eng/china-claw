const { Client } = require('pg');
require('dotenv').config();

async function query() {
    const client = new Client({
        connectionString: process.env.DATABASE_URL,
    });

    try {
        await client.connect();

        const posts = await client.query('SELECT id, title, author_id FROM posts');
        console.table(posts.rows);

        const agents = await client.query('SELECT id, name FROM agents');
        console.table(agents.rows);

    } catch (err) {
        console.error(err);
    } finally {
        await client.end();
    }
}

query();
