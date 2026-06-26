module.exports = {
  apps: [{
    name: "exposys-cert-api",
    script: "./server.js",
    cwd: "/var/www/exposys/certificate_system/backend",
    instances: 1,
    autorestart: true,
    watch: false,
    max_memory_restart: '1G',
    env: {
      NODE_ENV: "production",
      PORT: 3000
    }
  }]
};
