-- Create a table for job openings in schema human_resources, with an automatic ID, name, job description, evaluation criteria, create and update dates and users
CREATE TABLE IF NOT EXISTS
  "human_resources"."openings" ( 
    "id" SERIAL PRIMARY KEY,
    "name" VARCHAR(255),
    "job_description" TEXT,
    "evaluation_criteria" TEXT,
    "created_at" TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    "updated_at" TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    "created_by" VARCHAR(255),
    "updated_by" VARCHAR(255) 
  );