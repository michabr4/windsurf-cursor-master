import request from 'supertest';

describe('ServiceFlow SDM API', () => {
  let app: import('express').Express;
  let accessToken = '';

  beforeAll(async () => {
    process.env.NODE_ENV = 'test';
    process.env.PORT = '3005';
    process.env.JWT_SECRET = 'test_jwt_secret_at_least_32_chars_long_123';
    process.env.JWT_REFRESH_SECRET = 'test_refresh_secret_at_least_32_chars_123';
    process.env.BOOTSTRAP_ADMIN_EMAIL = 'admin@serviceflow.local';
    process.env.BOOTSTRAP_ADMIN_PASSWORD = 'A_Strong_Test_Password_123!';
    process.env.CORS_ORIGIN = 'http://localhost:8080';

    const mod = await import('../src/app');
    app = await mod.createApp();
  });

  it('GET /api/v1/health returns healthy', async () => {
    const response = await request(app).get('/api/v1/health');
    expect(response.status).toBe(200);
    expect(response.body.status).toBe('ok');
  });

  it('POST /api/v1/auth/login issues tokens', async () => {
    const response = await request(app).post('/api/v1/auth/login').send({
      email: 'admin@serviceflow.local',
      password: 'A_Strong_Test_Password_123!',
    });
    expect(response.status).toBe(200);
    expect(response.body.accessToken).toBeTruthy();
    accessToken = response.body.accessToken;
  });

  it('rejects property create when unauthenticated', async () => {
    const response = await request(app).post('/api/v1/properties').send({
      propertyCode: 'MGM-LV',
      propertyName: 'MGM Las Vegas',
      city: 'Las Vegas',
      state: 'NV',
    });
    expect(response.status).toBe(401);
  });

  it('creates property, device, incident and links TAC', async () => {
    const propertyRes = await request(app)
      .post('/api/v1/properties')
      .set('Authorization', `Bearer ${accessToken}`)
      .send({
        propertyCode: 'MGM-LV',
        propertyName: 'MGM Las Vegas',
        city: 'Las Vegas',
        state: 'NV',
      });
    expect(propertyRes.status).toBe(201);
    const propertyId = propertyRes.body.data.propertyId;

    const deviceRes = await request(app)
      .post('/api/v1/devices')
      .set('Authorization', `Bearer ${accessToken}`)
      .send({
        propertyId,
        hostname: 'core-sw-01',
        serialNumber: 'FTX1234ABC',
        model: 'C9500',
        status: 'active',
      });
    expect(deviceRes.status).toBe(201);
    const deviceId = deviceRes.body.data.deviceId;

    const incidentRes = await request(app)
      .post('/api/v1/incidents')
      .set('Authorization', `Bearer ${accessToken}`)
      .send({
        propertyId,
        deviceId,
        title: 'Core switch instability',
        description: 'Intermittent packet loss observed',
        priority: 'P2',
      });
    expect(incidentRes.status).toBe(201);
    const incidentId = incidentRes.body.data.incidentId;

    const tacLinkRes = await request(app)
      .post(`/api/v1/incidents/${incidentId}/tac-link`)
      .set('Authorization', `Bearer ${accessToken}`)
      .send({
        tacCaseNumber: 'SR-123456789',
        tacSeverity: '2',
      });
    expect(tacLinkRes.status).toBe(200);
    expect(tacLinkRes.body.data.tacCase.caseNumber).toBe('SR-123456789');
  });
});

