# UserSessionKeep Component

## Location
`client/src/components/common/UserSessionKeep/`

## Files
| File | Purpose |
|------|---------|
| sessionTypes.ts | Types and service configurations |
| useServiceSession.ts | Custom React hook for session management |
| UserSessionKeep.tsx | Main banner component |
| index.ts | Public exports |

## How to Import
```tsx
import { UserSessionKeep } from '../common/UserSessionKeep';
```

Or from the common index:
```tsx
import { UserSessionKeep } from '../components/common';
```

## How to Use
```tsx
<UserSessionKeep 
  serviceName="cv-optimizer"
  onStartNew={() => console.log('Starting new')}
/>
```

## Props
| Prop | Type | Required | Description |
|------|------|----------|-------------|
| serviceName | string | YES | Service identifier from SERVICE_CONFIGS |
| onStartNew | function | NO | Callback after session is archived |

## Supported Services
| serviceName | Display Name | Continue URL |
|-------------|--------------|--------------|
| cv-optimizer | Perfect Your CV | /service/cv-optimizer/unified?cv_id={id} |
| xray-analyzer | Decode the Job Post | /service/understand-job/results/{id} |
| predict-questions | Predict the Questions | /service/predict-questions/smart/results/{id} |

## Component Behavior
1. Shows nothing while loading or if no active session exists
2. Displays blue banner when user has work in progress
3. "Continue" button navigates to saved session
4. "Start New" opens confirmation dialog
5. Confirmation dialog offers Cancel, Download (optional), and Start New
6. Starting new archives the session and calls onStartNew callback

## Backend API Endpoints Required
Each service needs:
- `GET /api/{service}/latest` - Returns latest non-archived session
- `POST /api/{service}/{id}/archive` - Sets session status to 'archived'

## How to Add New Service

### Step 1: Add config to sessionTypes.ts
```typescript
'new-service': {
  serviceName: 'new-service',
  displayName: 'New Service Name',
  apiEndpoint: '/api/new-service/latest',
  archiveEndpoint: '/api/new-service/sessions',
  getContinueUrl: (id) => `/service/new-service/results/${id}`,
  formatSummary: (data) => `${data.field} summary text`
}
```

### Step 2: Create backend endpoints
Add to your service's router:
```python
@router.get("/latest")
async def get_latest_session(token: str = Query(...)):
    # Return latest non-archived session for user
    
@router.post("/{id}/archive")
async def archive_session(id: int, token: str = Query(...)):
    # Set session status to 'archived'
```

### Step 3: Add status column to database table
```sql
ALTER TABLE your_table ADD COLUMN status VARCHAR(20) DEFAULT 'completed';
```

### Step 4: Use component in page
```tsx
<UserSessionKeep serviceName="new-service" />
```
