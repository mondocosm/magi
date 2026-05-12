# MAGI Pipeline - Cloud Service Architecture

## Overview

The MAGI Cloud Service is a **MAGI-as-a-Service (MaaS)** platform that provides video processing capabilities through a web-based interface and RESTful API. The service handles authentication, billing, and processing using CPU/GPU cloud resources.

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                         Frontend Layer                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │   React.js   │  │   Mobile App │  │   REST API   │          │
│  │   Web App    │  │  (Future)    │  │  (External)  │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                         API Gateway                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │   FastAPI    │  │   Rate Limit │  │   Load Bal.  │          │
│  │   Backend    │  │   (Redis)    │  │   (Nginx)    │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
└─────────────────────────────────────────────────────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        ▼                     ▼                     ▼
┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│  Auth Service│    │ Billing Svc  │    │Processing Svc│
│  (FastAPI)   │    │  (FastAPI)   │    │  (FastAPI)   │
└──────────────┘    └──────────────┘    └──────────────┘
        │                     │                     │
        ▼                     ▼                     ▼
┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│ PostgreSQL   │    │ PostgreSQL   │    │   Redis      │
│  (Users)     │    │  (Billing)   │    │  (Queue)     │
└──────────────┘    └──────────────┘    └──────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Cloud GPU Resources                           │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │   AWS EC2    │  │  RunPod      │  │  Vast.ai     │          │
│  │  (NVIDIA)    │  │  (NVIDIA)    │  │  (NVIDIA)    │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Storage Layer                                 │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │   AWS S3     │  │  CloudFront  │  │   CDN        │          │
│  │  (Files)     │  │  (Delivery)  │  │  (Global)    │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
└─────────────────────────────────────────────────────────────────┘
```

---

## Core Services

### 1. Authentication Service

**Purpose:** User registration, login, session management, and API access control.

**Features:**
- User registration (email/password, OAuth)
- User login (email/password, OAuth)
- JWT token generation and validation
- Password reset (email)
- Email verification
- Session management
- API key generation and management
- Role-based access control (RBAC)
- Two-factor authentication (2FA) - optional

**Technology Stack:**
- **Backend:** FastAPI
- **Database:** PostgreSQL
- **Authentication:** JWT (JSON Web Tokens)
- **OAuth:** Google, GitHub, Microsoft
- **2FA:** TOTP (Time-based One-Time Password)
- **Email:** SendGrid or AWS SES

**API Endpoints:**
```http
# User Registration
POST /api/v1/auth/register
POST /api/v1/auth/verify-email

# User Login
POST /api/v1/auth/login
POST /api/v1/auth/logout
POST /api/v1/auth/refresh

# Password Management
POST /api/v1/auth/forgot-password
POST /api/v1/auth/reset-password

# OAuth
GET /api/v1/auth/oauth/google
GET /api/v1/auth/oauth/github
GET /api/v1/auth/oauth/microsoft

# API Keys
GET /api/v1/auth/api-keys
POST /api/v1/auth/api-keys
DELETE /api/v1/auth/api-keys/{key_id}

# 2FA
POST /api/v1/auth/2fa/enable
POST /api/v1/auth/2fa/disable
POST /api/v1/auth/2fa/verify
```

**Database Schema:**
```sql
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    is_verified BOOLEAN DEFAULT FALSE,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE user_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    token VARCHAR(500) UNIQUE NOT NULL,
    expires_at TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE api_keys (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    key_name VARCHAR(100) NOT NULL,
    key_hash VARCHAR(500) UNIQUE NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_used_at TIMESTAMP
);

CREATE TABLE user_2fa (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    secret VARCHAR(255) NOT NULL,
    is_enabled BOOLEAN DEFAULT FALSE,
    backup_codes TEXT[],
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

---

### 2. Billing Service

**Purpose:** Subscription management, payment processing, usage tracking, and invoicing.

**Features:**
- Subscription management (Free, Pro, Enterprise)
- Payment processing (Stripe)
- Usage tracking (processing time, file size, API calls)
- Invoicing and receipts
- Payment history
- Usage analytics
- Cost estimation
- Auto-renewal management
- Refund processing
- Tax calculation

**Technology Stack:**
- **Backend:** FastAPI
- **Database:** PostgreSQL
- **Payment Processor:** Stripe
- **Invoicing:** Stripe Invoices
- **Analytics:** Custom analytics

**API Endpoints:**
```http
# Subscriptions
GET /api/v1/billing/subscription
POST /api/v1/billing/subscribe
PUT /api/v1/billing/subscription
DELETE /api/v1/billing/subscription
POST /api/v1/billing/subscription/cancel

# Payment Methods
GET /api/v1/billing/payment-methods
POST /api/v1/billing/payment-methods
DELETE /api/v1/billing/payment-methods/{method_id}

# Invoices
GET /api/v1/billing/invoices
GET /api/v1/billing/invoices/{invoice_id}

# Usage
GET /api/v1/billing/usage
GET /api/v1/billing/usage/current-month
GET /api/v1/billing/usage/history

# Pricing
GET /api/v1/billing/pricing
GET /api/v1/billing/estimate

# Webhooks (Stripe)
POST /api/v1/billing/webhooks/stripe
```

**Database Schema:**
```sql
CREATE TABLE subscriptions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    plan_type VARCHAR(50) NOT NULL, -- 'free', 'pro', 'enterprise'
    stripe_subscription_id VARCHAR(255),
    stripe_customer_id VARCHAR(255),
    status VARCHAR(50) NOT NULL, -- 'active', 'canceled', 'past_due', 'trialing'
    current_period_start TIMESTAMP,
    current_period_end TIMESTAMP,
    cancel_at_period_end BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE usage_records (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    job_id UUID,
    resource_type VARCHAR(50) NOT NULL, -- 'processing_time', 'file_size', 'api_calls'
    amount DECIMAL(10, 2) NOT NULL,
    unit VARCHAR(20) NOT NULL, -- 'minutes', 'bytes', 'calls'
    cost DECIMAL(10, 2) NOT NULL,
    recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE invoices (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    stripe_invoice_id VARCHAR(255) UNIQUE,
    amount DECIMAL(10, 2) NOT NULL,
    currency VARCHAR(3) DEFAULT 'USD',
    status VARCHAR(50) NOT NULL, -- 'draft', 'open', 'paid', 'void', 'uncollectible'
    due_date TIMESTAMP,
    paid_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE payment_methods (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    stripe_payment_method_id VARCHAR(255) UNIQUE,
    type VARCHAR(50) NOT NULL, -- 'card', 'bank_account'
    last4 VARCHAR(4),
    brand VARCHAR(20),
    expiry_month INTEGER,
    expiry_year INTEGER,
    is_default BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Pricing Tiers:**

| Feature | Free | Pro | Enterprise |
|---------|------|-----|------------|
| **Price** | $0/month | $9.99/month | $99.99/month |
| **File Size** | 100 MB | 2 GB | 10 GB |
| **Daily Conversions** | 3 | 50 | Unlimited |
| **Resolution** | 1080p | 4K | 8K |
| **Processing Time** | 5 min/job | 30 min/job | Unlimited |
| **API Calls** | 0 | 1,000/month | Unlimited |
| **Priority** | Standard | High | Highest |
| **Watermark** | Yes | No | No |
| **Support** | Email | Email (24h) | 24/7 Dedicated |
| **SLA** | None | None | 99.9% |

---

### 3. Processing Service

**Purpose:** Job management, GPU resource allocation, video processing, and result delivery.

**Features:**
- Job submission and management
- GPU resource allocation (AWS, RunPod, Vast.ai)
- Queue management (Redis)
- Progress tracking
- Real-time status updates
- Error handling and retry logic
- Cost tracking
- Auto-scaling based on demand
- Priority queue for paid users
- Batch processing support

**Technology Stack:**
- **Backend:** FastAPI
- **Queue:** Redis + Celery
- **GPU Providers:** AWS EC2, RunPod, Vast.ai
- **Storage:** AWS S3
- **Monitoring:** Custom monitoring

**API Endpoints:**
```http
# Video Processing
POST /api/v1/video/convert
GET /api/v1/video/status/{job_id}
GET /api/v1/video/download/{job_id}
DELETE /api/v1/video/cancel/{job_id}
GET /api/v1/video/jobs

# Camera Processing
POST /api/v1/camera/start
POST /api/v1/camera/stop
GET /api/v1/camera/status/{session_id}
GET /api/v1/camera/stream/{session_id}

# Game Processing
POST /api/v1/game/start
POST /api/v1/game/stop
GET /api/v1/game/status/{session_id}
GET /api/v1/game/stream/{session_id}

# Batch Processing
POST /api/v1/batch/create
GET /api/v1/batch/status/{batch_id}
GET /api/v1/batch/download/{batch_id}

# GPU Resources
GET /api/v1/resources/gpu/available
GET /api/v1/resources/gpu/usage
GET /api/v1/resources/gpu/costs
```

**Database Schema:**
```sql
CREATE TABLE jobs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    job_type VARCHAR(50) NOT NULL, -- 'video', 'camera', 'game', 'batch'
    status VARCHAR(50) NOT NULL, -- 'pending', 'processing', 'completed', 'failed', 'cancelled'
    input_file_url VARCHAR(500),
    output_file_url VARCHAR(500),
    settings JSONB,
    gpu_provider VARCHAR(50), -- 'aws', 'runpod', 'vastai'
    gpu_instance_id VARCHAR(255),
    processing_time_seconds INTEGER,
    cost DECIMAL(10, 2),
    error_message TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    started_at TIMESTAMP,
    completed_at TIMESTAMP
);

CREATE TABLE job_progress (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    job_id UUID REFERENCES jobs(id),
    stage VARCHAR(50) NOT NULL, -- 'upload', 'analysis', 'interpolation', 'upscaling', 'encoding', 'download'
    progress INTEGER NOT NULL, -- 0-100
    message TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE gpu_instances (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    provider VARCHAR(50) NOT NULL,
    instance_id VARCHAR(255) NOT NULL,
    instance_type VARCHAR(100) NOT NULL, -- 'NVIDIA A100', 'RTX 4090', etc.
    gpu_count INTEGER NOT NULL,
    status VARCHAR(50) NOT NULL, -- 'available', 'busy', 'maintenance'
    current_job_id UUID REFERENCES jobs(id),
    hourly_cost DECIMAL(10, 2) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Job Processing Pipeline:**

```
1. Job Submission
   ↓
2. Validation (file size, format, user quota)
   ↓
3. Queue Assignment (based on user tier)
   ↓
4. GPU Resource Allocation
   ↓
5. File Download (from S3)
   ↓
6. Video Analysis (format, resolution, frame rate)
   ↓
7. 2D to 3D Conversion (if needed)
   ↓
8. Frame Interpolation (to 120 fps)
   ↓
9. Upscaling (to 4K per eye)
   ↓
10. Frame Cadence (left/right eye alternating)
    ↓
11. MAGI Encoding (HEVC H.265)
    ↓
12. File Upload (to S3)
    ↓
13. Job Completion
    ↓
14. Notification (email, webhook)
    ↓
15. GPU Resource Release
```

---

## Cloud GPU Integration

### Supported Providers

#### 1. AWS EC2 (Primary)
- **Instance Types:** p3.2xlarge, p3.8xlarge, p3.16xlarge, g4dn.xlarge, g4dn.2xlarge
- **GPU:** NVIDIA V100, T4
- **Pricing:** $3.06 - $31.61/hour
- **Pros:** Reliable, scalable, integrated with AWS services
- **Cons:** Higher cost, longer startup time

#### 2. RunPod (Secondary)
- **Instance Types:** NVIDIA A100, RTX 4090, RTX 3090
- **Pricing:** $0.20 - $2.00/hour
- **Pros:** Lower cost, faster startup, GPU marketplace
- **Cons:** Less reliable, limited availability

#### 3. Vast.ai (Tertiary)
- **Instance Types:** Various NVIDIA GPUs
- **Pricing:** $0.10 - $1.00/hour
- **Pros:** Lowest cost, wide selection
- **Cons:** Variable quality, peer-to-peer

### GPU Selection Logic

```python
def select_gpu(user_tier, job_requirements):
    """
    Select GPU based on user tier and job requirements
    """
    if user_tier == 'enterprise':
        # Enterprise users get best GPUs
        if job_requirements['resolution'] == '8K':
            return {'provider': 'aws', 'instance': 'p3.16xlarge'}
        else:
            return {'provider': 'runpod', 'instance': 'NVIDIA A100'}
    
    elif user_tier == 'pro':
        # Pro users get good GPUs
        if job_requirements['resolution'] == '4K':
            return {'provider': 'runpod', 'instance': 'RTX 4090'}
        else:
            return {'provider': 'vastai', 'instance': 'RTX 3090'}
    
    else:  # free tier
        # Free users get basic GPUs
        return {'provider': 'vastai', 'instance': 'RTX 3060'}
```

---

## Security

### Authentication & Authorization
- JWT tokens for API authentication
- API keys for external integrations
- Role-based access control (RBAC)
- Rate limiting (per user tier)
- IP whitelisting (enterprise)

### Data Security
- Encryption at rest (AES-256)
- Encryption in transit (TLS 1.3)
- Secure file storage (S3 with encryption)
- Automatic file deletion (after 7 days)
- GDPR compliance

### Payment Security
- PCI DSS compliance (via Stripe)
- Secure payment processing
- Fraud detection
- Refund protection

---

## Monitoring & Analytics

### Metrics
- Job success rate
- Average processing time
- GPU utilization
- Cost per job
- User engagement
- Revenue tracking

### Alerts
- Job failures
- GPU unavailability
- Payment failures
- High error rates
- Cost overruns

### Logging
- Application logs
- Access logs
- Error logs
- Performance logs
- Security logs

---

## Deployment

### Infrastructure
- **Hosting:** AWS (us-east-1)
- **Database:** AWS RDS PostgreSQL
- **Cache:** AWS ElastiCache Redis
- **Storage:** AWS S3
- **CDN:** AWS CloudFront
- **Load Balancer:** AWS ALB
- **Monitoring:** AWS CloudWatch

### CI/CD
- **Version Control:** GitHub
- **CI:** GitHub Actions
- **CD:** AWS CodeDeploy
- **Container:** Docker
- **Orchestration:** Kubernetes (optional)

---

## Cost Estimation

### Monthly Costs (Estimated)

| Service | Free Tier | Pro Tier | Enterprise |
|---------|-----------|----------|------------|
| **AWS EC2** | $0 | $500 | $5,000 |
| **AWS RDS** | $50 | $100 | $500 |
| **AWS ElastiCache** | $30 | $50 | $200 |
| **AWS S3** | $20 | $100 | $500 |
| **AWS CloudFront** | $10 | $50 | $200 |
| **Stripe Fees** | 0% | 2.9% | 2.9% |
| **Total** | $110 | $800 | $6,400 |

### Revenue vs Cost

| Tier | Monthly Revenue | Monthly Cost | Profit |
|------|-----------------|--------------|--------|
| **Free** | $0 | $110 | -$110 |
| **Pro** | $9.99 | $0.80 | $9.19 |
| **Enterprise** | $99.99 | $6.40 | $93.59 |

**Break-even Analysis:**
- Need ~12 Pro users to cover Free tier costs
- Need ~7 Enterprise users to cover all costs
- Mixed model: 100 Free + 50 Pro + 10 Enterprise = $1,500 revenue - $1,100 cost = $400 profit

---

## Next Steps

1. **Phase 1: Core Infrastructure** (Month 4)
   - Set up AWS infrastructure
   - Deploy FastAPI backend
   - Set up PostgreSQL database
   - Set up Redis cache
   - Set up S3 storage

2. **Phase 2: Authentication Service** (Month 4)
   - Implement user registration/login
   - Implement JWT authentication
   - Implement OAuth integration
   - Implement API key management

3. **Phase 3: Billing Service** (Month 5)
   - Integrate Stripe
   - Implement subscription management
   - Implement usage tracking
   - Implement invoicing

4. **Phase 4: Processing Service** (Month 5)
   - Implement job queue
   - Integrate GPU providers
   - Implement processing pipeline
   - Implement progress tracking

5. **Phase 5: Frontend** (Month 6)
   - Develop React.js web app
   - Implement user dashboard
   - Implement file upload
   - Implement progress visualization

6. **Phase 6: Testing & Launch** (Month 6)
   - Beta testing
   - Performance optimization
   - Security audit
   - Public launch

---

## Conclusion

The MAGI Cloud Service provides a complete MAGI-as-a-Service platform with authentication, billing, and processing services. The service is designed to be scalable, secure, and cost-effective, with multiple pricing tiers to meet different user needs.

**Key Features:**
- ✅ Secure authentication (JWT, OAuth, 2FA)
- ✅ Flexible billing (Stripe, subscriptions, usage-based)
- ✅ Scalable processing (AWS, RunPod, Vast.ai)
- ✅ Real-time progress tracking
- ✅ Multiple pricing tiers (Free, Pro, Enterprise)
- ✅ RESTful API for integration
- ✅ Modern web interface

**The MAGI Cloud Service will make MAGI processing accessible to everyone, from casual users to enterprise customers!** 🚀
