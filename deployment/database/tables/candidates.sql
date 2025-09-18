-- Create a table for candidates in schema human_resources, with an automatic ID, name, email, cv_text, create and update dates and users
CREATE TABLE IF NOT EXISTS
  "human_resources"."candidates" ( 
    "id" SERIAL PRIMARY KEY,
    "name" VARCHAR(255),
    "email" VARCHAR(255),
    "content" TEXT,
    "created_at" TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    "updated_at" TIMESTAMP WITH TIME ZONE DEFAULT NOW()
  );