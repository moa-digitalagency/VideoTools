import type { Express, Request, Response } from "express";
import { createServer, type Server } from "http";
import http from "http";
import multer from "multer";
import path from "path";
import fs from "fs";
import { spawn, ChildProcess } from "child_process";

const FLASK_HOST = "localhost";
const FLASK_PORT = 5001;

let flaskProcess: ChildProcess | null = null;

function startFlaskServer() {
  if (flaskProcess) return;
  
  console.log("Starting Flask backend server...");
  flaskProcess = spawn("python", ["server/app.py"], {
    stdio: ["ignore", "pipe", "pipe"],
    detached: false,
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

const UPLOAD_DIR = path.join(process.cwd(), "uploads");
if (!fs.existsSync(UPLOAD_DIR)) {
  fs.mkdirSync(UPLOAD_DIR, { recursive: true });
}

const upload = multer({
  storage: multer.diskStorage({
    destination: (_req, _file, cb) => cb(null, UPLOAD_DIR),
    filename: (_req, file, cb) => {
      const uniqueSuffix = Date.now() + "-" + Math.round(Math.random() * 1e9);
      cb(null, uniqueSuffix + path.extname(file.originalname));
    },
  }),
  limits: { fileSize: 500 * 1024 * 1024 },
});

function proxyToFlask(req: Request, res: Response, method: string, path: string, body?: any) {
  const options: http.RequestOptions = {
    hostname: FLASK_HOST,
    port: FLASK_PORT,
    path: path,
    method: method,
    headers: {
      "Content-Type": "application/json",
    },
  };

  const proxyReq = http.request(options, (proxyRes) => {
    res.status(proxyRes.statusCode || 200);
    
    const contentType = proxyRes.headers["content-type"];
    if (contentType) {
      res.setHeader("Content-Type", contentType);
    }
    
    if (contentType?.includes("application/octet-stream") || 
        proxyRes.headers["content-disposition"]) {
      if (proxyRes.headers["content-disposition"]) {
        res.setHeader("Content-Disposition", proxyRes.headers["content-disposition"]);
      }
      proxyRes.pipe(res);
    } else {
      let data = "";
      proxyRes.on("data", (chunk) => {
        data += chunk;
      });
      proxyRes.on("end", () => {
        try {
          res.json(JSON.parse(data));
        } catch {
          res.send(data);
        }
      });
    }
  });

  proxyReq.on("error", (error) => {
    console.error("Proxy error:", error);
    res.status(502).json({ error: "Backend service unavailable" });
  });

  if (body) {
    proxyReq.write(JSON.stringify(body));
  }
  
  proxyReq.end();
}

export async function registerRoutes(
  httpServer: Server,
  app: Express
): Promise<Server> {
  
  startFlaskServer();
  
  await new Promise(resolve => setTimeout(resolve, 2000));
  
  app.get("/api/videos", (req, res) => {
    proxyToFlask(req, res, "GET", "/api/videos");
  });

  app.post("/api/videos/upload", upload.single("video"), async (req: Request, res: Response) => {
    if (!req.file) {
      return res.status(400).json({ error: "No video file provided" });
    }

    const FormData = (await import("form-data")).default;
    const formData = new FormData();
    formData.append("video", fs.createReadStream(req.file.path), {
      filename: req.file.originalname,
      contentType: req.file.mimetype,
    });

    const options: http.RequestOptions = {
      hostname: FLASK_HOST,
      port: FLASK_PORT,
      path: "/api/videos/upload",
      method: "POST",
      headers: formData.getHeaders(),
    };

    const proxyReq = http.request(options, (proxyRes) => {
      let data = "";
      proxyRes.on("data", (chunk) => {
        data += chunk;
      });
      proxyRes.on("end", () => {
        fs.unlinkSync(req.file!.path);
        try {
          res.status(proxyRes.statusCode || 200).json(JSON.parse(data));
        } catch {
          res.status(proxyRes.statusCode || 200).send(data);
        }
      });
    });

    proxyReq.on("error", (error) => {
      console.error("Upload proxy error:", error);
      res.status(502).json({ error: "Backend service unavailable" });
    });

    formData.pipe(proxyReq);
  });

  app.delete("/api/videos/:id", (req, res) => {
    proxyToFlask(req, res, "DELETE", `/api/videos/${req.params.id}`);
  });

  app.get("/api/videos/:id/download", (req, res) => {
    const options: http.RequestOptions = {
      hostname: FLASK_HOST,
      port: FLASK_PORT,
      path: `/api/videos/${req.params.id}/download`,
      method: "GET",
    };

    const proxyReq = http.request(options, (proxyRes) => {
      res.status(proxyRes.statusCode || 200);
      Object.entries(proxyRes.headers).forEach(([key, value]) => {
        if (value) res.setHeader(key, value);
      });
      proxyRes.pipe(res);
    });

    proxyReq.on("error", (error) => {
      console.error("Download proxy error:", error);
      res.status(502).json({ error: "Backend service unavailable" });
    });

    proxyReq.end();
  });

  app.post("/api/videos/split", (req, res) => {
    proxyToFlask(req, res, "POST", "/api/videos/split", req.body);
  });

  app.post("/api/videos/merge", (req, res) => {
    proxyToFlask(req, res, "POST", "/api/videos/merge", req.body);
  });

  app.get("/api/jobs", (req, res) => {
    proxyToFlask(req, res, "GET", "/api/jobs");
  });

  app.get("/api/jobs/:id/download", (req, res) => {
    const options: http.RequestOptions = {
      hostname: FLASK_HOST,
      port: FLASK_PORT,
      path: `/api/jobs/${req.params.id}/download`,
      method: "GET",
    };

    const proxyReq = http.request(options, (proxyRes) => {
      res.status(proxyRes.statusCode || 200);
      Object.entries(proxyRes.headers).forEach(([key, value]) => {
        if (value) res.setHeader(key, value);
      });
      proxyRes.pipe(res);
    });

    proxyReq.on("error", (error) => {
      console.error("Job download proxy error:", error);
      res.status(502).json({ error: "Backend service unavailable" });
    });

    proxyReq.end();
  });

  app.get("/api/stats", (req, res) => {
    proxyToFlask(req, res, "GET", "/api/stats");
  });

  return httpServer;
}
