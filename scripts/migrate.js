const { Client } = require('pg');
const fs = require('fs');
const path = require('path');
require('dotenv').config();

// Enable detailed logging
const verbose = process.argv.includes('--verbose');

async function migrate() {
    console.log('🔄 Starting database migration...');
    console.log('📝 Reading schema.sql...');

    const client = new Client({
        connectionString: process.env.DATABASE_URL,
    });

    try {
        await client.connect();
        console.log('✅ Connected to database at ' + process.env.DATABASE_URL.replace(/:[^:@]*@/, ':****@')); // Hide password in logs

        const schemaPath = path.join(__dirname, 'schema.sql');
        if (!fs.existsSync(schemaPath)) {
            throw new Error(`Schema file not found at ${schemaPath}`);
        }

        const schema = fs.readFileSync(schemaPath, 'utf8');

        console.log('⚡ Executing schema...');
        // Split commands by semicolon just in case, or run as whole block?
        // Running as whole block usually works for pg unless there are specific transaction blocks issues, 
        // but this schema has simple CREATE TABLE statements.
        await client.query(schema);

        console.log('✅ Database schema applied successfully!');
        console.log('✅ Created default submolt "general"');

    } catch (err) {
        if (err.code === '42P07') {
            console.warn('⚠️  Some tables already exist. Migration might be partial.');
        } else {
            console.error('❌ Migration failed:', err.message);
            if (verbose) console.error(err);
        }
        process.exit(1);
    } finally {
        await client.end();
    }
}

migrate();
