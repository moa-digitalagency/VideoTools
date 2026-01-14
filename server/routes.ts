import type { Express, Request, Response } from "express";
import { createServer, type Server } from "http";
import http from "http";
import { spawn, ChildProcess } from "child_process";

const FLASK_HOST = "localhost";
const FLASK_PORT = 5001;

let flaskProcess: ChildProcess | null = null;

function startFlaskServer() {
  if (flaskProcess) return;
  
  console.log("Starting Flask backend server on port 5001...");
  flaskProcess = spawn("python", ["server/app.py"], {
    stdio: ["ignore", "pipe", "pipe"],
    detached: false,
    env: { ...process.env, FLASK_PORT: "5001" }
  });
  
  flaskProcess.stdout?.on("data", (data) => {
    console.log(`[Flask] ${data.toString().trim()}`);
  });
  
  flaskProcess.stderr?.on("data", (data) => {
    console.log(`[Flask] ${data.toString().trim()}`);
  });
  
  flaskProcess.on("error", (err) => {
    console.error("Failed to start Flask:", err);
  });
  
  flaskProcess.on("exit", (code) => {
    console.log(`Flask exited with code ${code}`);
    flaskProcess = null;
  });
  
  process.on("exit", () => {
    if (flaskProcess) {
      flaskProcess.kill();
    }
  });
}

function proxyToFlask(req: Request, res: Response) {
  const options: http.RequestOptions = {
    hostname: FLASK_HOST,
    port: FLASK_PORT,
    path: req.url,
    method: req.method,
    headers: { ...req.headers as any, host: `${FLASK_HOST}:${FLASK_PORT}` },
  };

  const proxyReq = http.request(options, (proxyRes) => {
    res.status(proxyRes.statusCode || 200);
    
    Object.keys(proxyRes.headers).forEach(key => {
      const val = proxyRes.headers[key];
      if (val) res.setHeader(key, val);
    });
    
    proxyRes.pipe(res);
  });

  proxyReq.on("error", (err) => {
    console.error("Proxy error:", err);
    res.status(502).json({ error: "Backend unavailable" });
  });

  req.pipe(proxyReq);
}

export async function registerRoutes(
  httpServer: Server,
  app: Express
): Promise<Server> {
  
  startFlaskServer();
  
  await new Promise(resolve => setTimeout(resolve, 2000));
  
  app.all("*", (req, res) => {
    proxyToFlask(req, res);
  });

  return httpServer;
}
