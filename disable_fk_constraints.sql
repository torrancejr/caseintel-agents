-- Temporarily disable foreign key constraints for local testing
-- This allows testing the agents API without having document records in the backend

-- Drop the foreign key constraint on analysis_jobs.document_id
ALTER TABLE analysis_jobs DROP CONSTRAINT IF EXISTS analysis_jobs_document_id_fkey;

-- Drop the foreign key constraint on analysis_results.document_id  
ALTER TABLE analysis_results DROP CONSTRAINT IF EXISTS analysis_results_document_id_fkey;

-- Drop the foreign key constraint on agent_timeline_events.document_id
ALTER TABLE agent_timeline_events DROP CONSTRAINT IF EXISTS agent_timeline_events_document_id_fkey;

-- Drop the foreign key constraint on witness_mentions.document_id
ALTER TABLE witness_mentions DROP CONSTRAINT IF EXISTS witness_mentions_document_id_fkey;

-- Verify constraints were dropped
SELECT 
    conname AS constraint_name,
    conrelid::regclass AS table_name
FROM pg_constraint
WHERE conname LIKE '%document_id%'
AND contype = 'f';

-- Expected: No rows (all document_id foreign keys removed)
