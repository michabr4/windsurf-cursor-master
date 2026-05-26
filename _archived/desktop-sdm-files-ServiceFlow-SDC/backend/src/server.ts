import { createApp } from './app';
import { config } from './config';

async function main() {
  const app = await createApp();
  app.listen(config.PORT, () => {
    console.log(`ServiceFlow SDM backend listening on port ${config.PORT}`);
  });
}

main().catch((err) => {
  console.error('Failed to start server:', err);
  process.exit(1);
});

