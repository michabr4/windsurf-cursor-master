import cors from 'cors';
import express from 'express';
import helmet from 'helmet';
import morgan from 'morgan';
import { config } from './config';
import { requestContext, errorHandler, notFound } from './middleware';
import { buildRouter } from './routes';
import { queueManager } from './queues';
import { store } from './store';

export async function createApp() {
  await store.init();
  queueManager.init();
  const app = express();
  const corsOrigins = (config.CORS_ORIGIN ?? '')
    .split(',')
    .map((x) => x.trim())
    .filter(Boolean);

  app.use(helmet());
  app.use(express.json({ limit: '1mb' }));
  app.use(requestContext);
  app.use(
    cors({
      origin: corsOrigins.length > 0 ? corsOrigins : true,
      credentials: true,
    }),
  );
  app.use(morgan('combined'));

  app.use('/api/v1', buildRouter());
  app.use(notFound);
  app.use(errorHandler);

  return app;
}

