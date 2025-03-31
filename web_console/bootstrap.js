#!/usr/bin/env node

const Router = require('@koa/router');
const Next = require('next');
const grpc = require('@grpc/grpc-js');
const { Op } = require('sequelize');
const SessionMiddleware = require('./middlewares/session');
const models = require('./models');
const server = require('./server');
const rpcServer = require('./rpc/server');
const getConfig = require('./utils/get_confg');

const config = getConfig({
  DB_SYNC: process.env.DB_SYNC,
});

const env = process.env.NODE_ENV || 'development';
const renderer = Next({
  dev: env === 'development',
});

async function setupDatabase() {
  if (config.DB_SYNC === 'true') {
    await models.sequelize.sync();
    return models.User.findOrCreate({
      where: {
        username: { [Op.eq]: 'ada' },
      },
      defaults: {
        username: 'ada',
        password: 'fdee430d40bd57de',
        name: 'Ada',
        is_admin: true,
      },
    });
  }
}

async function setupNextRoutes() {
  const router = new Router();
  const handle = renderer.getRequestHandler();

  router.all('*', SessionMiddleware, async (ctx) => {
    await handle(ctx.req, ctx.res);
    ctx.respond = false;
  });

  server.use(async (ctx, next) => {
    ctx.res.statusCode = 200;
    await next();
  });

  server.use(router.routes(), router.allowedMethods());
}

function startRpcServer() {
  const host = process.env.GRPC_HOST || '0.0.0.0';
  const port = parseInt(process.env.GRPC_PORT, 10) || 1990;
  rpcServer.bindAsync(
    `${host}:${port}`,
    grpc.ServerCredentials.createInsecure(),
    (err) => {
      if (err) process.exit(1);
      rpcServer.start();
      console.log(`> RPC Server is ready on http://${host}:${port}`);
    },
  );
}

function bootstrap() {
  const host = process.env.HOST || '0.0.0.0';
  const port = parseInt(process.env.PORT, 10) || 1989;
  server.listen(port, () => {
    console.log(`> Web Console Server is ready on http://${host}:${port}`);
    startRpcServer();
  });
}

renderer.prepare()
  .then(() => setupDatabase())
  .then(() => setupNextRoutes())
  .then(() => bootstrap());
