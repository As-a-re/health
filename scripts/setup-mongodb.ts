import { MongoClient } from "mongodb"

const MONGODB_URL = process.env.MONGODB_URL || "mongodb://localhost:27017/akan_health_db"

async function setupMongoDB() {
  console.log("🚀 Setting up MongoDB for Akan Health Assistant...")

  const client = new MongoClient(MONGODB_URL)

  try {
    await client.connect()
    console.log("✅ Connected to MongoDB")

    const db = client.db()

    // Create collections and indexes
    const collections = [
      {
        name: "users",
        indexes: [{ key: { email: 1 }, unique: true }, { key: { created_at: -1 } }, { key: { preferred_language: 1 } }],
      },
      {
        name: "health_queries",
        indexes: [
          { key: { user_id: 1 } },
          { key: { created_at: -1 } },
          { key: { query_language: 1 } },
          { key: { response_language: 1 } },
        ],
      },
      {
        name: "query_logs",
        indexes: [{ key: { timestamp: -1 } }, { key: { user_id: 1 } }, { key: { query_id: 1 } }, { key: { type: 1 } }],
      },
      {
        name: "error_logs",
        indexes: [{ key: { timestamp: -1 } }, { key: { user_id: 1 } }, { key: { type: 1 } }],
      },
      {
        name: "medical_knowledge",
        indexes: [{ key: { version: 1 } }, { key: { created_at: -1 } }],
      },
    ]

    for (const collection of collections) {
      // Create collection if it doesn't exist
      const collectionExists = await db.listCollections({ name: collection.name }).hasNext()
      if (!collectionExists) {
        await db.createCollection(collection.name)
        console.log(`✅ Created collection: ${collection.name}`)
      }

      // Create indexes
      for (const index of collection.indexes) {
        try {
          await db.collection(collection.name).createIndex(index.key, {
            unique: index.unique || false,
          })
          console.log(`✅ Created index for ${collection.name}:`, index.key)
        } catch (error: any) {
          if (error.code !== 11000) {
            // Ignore duplicate key errors
            console.warn(`⚠️ Failed to create index for ${collection.name}:`, error.message)
          }
        }
      }
    }

    console.log("✅ MongoDB setup completed successfully!")
  } catch (error) {
    console.error("❌ MongoDB setup failed:", error)
    process.exit(1)
  } finally {
    await client.close()
  }
}

if (require.main === module) {
  setupMongoDB()
}

export { setupMongoDB }
