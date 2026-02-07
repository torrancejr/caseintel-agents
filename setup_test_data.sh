#!/bin/bash

echo "📝 Creating test data in database..."

psql $DATABASE_URL << 'EOF'
-- Create test firm
INSERT INTO firms (id, name, "createdAt", "updatedAt", plan_code, included_seats, extra_seats, extra_seat_price_cents)
VALUES (
  '00000000-0000-0000-0000-000000000001',
  'Test Law Firm',
  NOW(),
  NOW(),
  'free',
  5,
  0,
  0
)
ON CONFLICT (id) DO UPDATE SET
  name = EXCLUDED.name,
  "updatedAt" = NOW();

-- Create test user
INSERT INTO users (id, email, "passwordHash", role, "firstName", "lastName", firm_id, "createdAt", "updatedAt", "betaAccessGranted", firm_role, is_active, user_type, email_verified, two_factor_enabled, system_role)
VALUES (
  '00000000-0000-0000-0000-000000000002',
  'test@testfirm.com',
  '$2b$10$dummyhashfortest',
  'attorney',
  'Test',
  'User',
  '00000000-0000-0000-0000-000000000001',
  NOW(),
  NOW(),
  false,
  'ATTORNEY',
  true,
  'standard',
  true,
  false,
  'USER'
)
ON CONFLICT (id) DO NOTHING;

-- Create test case 1
INSERT INTO cases (id, title, matter_number, firm_id, created_by, created_at, updated_at, status, is_deleted, portal_enabled)
VALUES (
  '00000000-0000-0000-0000-000000000001',
  'Product Liability Case',
  '2024-PL-001',
  '00000000-0000-0000-0000-000000000001',
  '00000000-0000-0000-0000-000000000002',
  NOW(),
  NOW(),
  'DISCOVERY',
  false,
  false
)
ON CONFLICT (id) DO NOTHING;

-- Create test case 2
INSERT INTO cases (id, title, matter_number, firm_id, created_by, created_at, updated_at, status, is_deleted, portal_enabled)
VALUES (
  '00000000-0000-0000-0000-000000000002',
  'Employment Settlement Case',
  '2024-ES-002',
  '00000000-0000-0000-0000-000000000001',
  '00000000-0000-0000-0000-000000000002',
  NOW(),
  NOW(),
  'SETTLEMENT',
  false,
  false
)
ON CONFLICT (id) DO NOTHING;

-- Create test document 1
INSERT INTO documents (id, original_filename, storage_key, mime_type, size_bytes, status, case_id, uploaded_by, uploaded_at, updated_at, download_allowed)
VALUES (
  '00000000-0000-0000-0000-000000000011',
  'Product Liability Email.txt',
  'local/test_email_1.txt',
  'text/plain',
  1024,
  'processed',
  '00000000-0000-0000-0000-000000000001',
  '00000000-0000-0000-0000-000000000002',
  NOW(),
  NOW(),
  true
)
ON CONFLICT (id) DO NOTHING;

-- Create test document 2
INSERT INTO documents (id, original_filename, storage_key, mime_type, size_bytes, status, case_id, uploaded_by, uploaded_at, updated_at, download_allowed)
VALUES (
  '00000000-0000-0000-0000-000000000022',
  'Settlement Agreement.txt',
  'local/test_contract_2.txt',
  'text/plain',
  2048,
  'processed',
  '00000000-0000-0000-0000-000000000002',
  '00000000-0000-0000-0000-000000000002',
  NOW(),
  NOW(),
  true
)
ON CONFLICT (id) DO NOTHING;

SELECT 'Test data created successfully!' as status;
EOF

echo "✅ Test data created!"
