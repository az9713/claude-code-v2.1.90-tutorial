#!/usr/bin/env bash
# mcp_doctor.sh - Diagnose broken MCP server configurations
# Works on Windows (Git Bash/MSYS2), macOS, and Linux
# Scans all known MCP config sources (omp, claude, cursor, windsurf, gemini, codex, vscode)
# Outputs JSON array of { name, status, reason, command, source } per server

set -euo pipefail

# Use node for JSON parsing, multi-source discovery, and PATH-based binary lookup
node -e '
const fs = require("fs");
const path = require("path");
const os = require("os");

const HOME = os.homedir();

// All known MCP config sources with priority (higher = wins on name conflict)
const CONFIG_SOURCES = [
   { name: "omp-user",    priority: 100, path: path.join(HOME, ".omp", "agent", "mcp.json"), format: "mcpServers" },
   { name: "claude-user",  priority: 80,  path: path.join(HOME, ".claude", "mcp.json"),       format: "mcpServers" },
   { name: "cursor-user",  priority: 50,  path: path.join(HOME, ".cursor", "mcp.json"),       format: "mcpServers" },
   { name: "windsurf-user", priority: 50, path: path.join(HOME, ".codeium", "windsurf", "mcp_config.json"), format: "mcpServers" },
];

// Project-level configs (check cwd)
const cwd = process.cwd();
const PROJECT_SOURCES = [
   { name: "omp-project",    priority: 100, path: path.join(cwd, ".omp", "mcp.json"),       format: "mcpServers" },
   { name: "claude-project", priority: 80,  path: path.join(cwd, ".claude", "mcp.json"),     format: "mcpServers" },
   { name: "cursor-project", priority: 50,  path: path.join(cwd, ".cursor", "mcp.json"),     format: "mcpServers" },
   { name: "vscode-project", priority: 20,  path: path.join(cwd, ".vscode", "mcp.json"),     format: "mcp.servers" },
];

const ALL_SOURCES = [...CONFIG_SOURCES, ...PROJECT_SOURCES];

function findInPath(cmd) {
   const dirs = (process.env.PATH || "").split(path.delimiter);
   const isWin = process.platform === "win32";
   const exts = isWin
      ? (process.env.PATHEXT || ".COM;.EXE;.BAT;.CMD;.JS").toLowerCase().split(";")
      : [""];

   for (const dir of dirs) {
      for (const ext of exts) {
         const full = path.join(dir, cmd + ext);
         try { fs.accessSync(full, fs.constants.X_OK); return full; } catch {}
      }
      if (!isWin) {
         const full = path.join(dir, cmd);
         try { fs.accessSync(full, fs.constants.X_OK); return full; } catch {}
      }
   }
   return null;
}

function checkBinary(bin) {
   if (path.isAbsolute(bin)) {
      return fs.existsSync(bin) ? { ok: true, path: bin } : { ok: false };
   }
   const found = findInPath(bin);
   return found ? { ok: true, path: found } : { ok: false };
}

function checkDocker() {
   try {
      require("child_process").execSync("docker info", {
         stdio: "pipe",
         timeout: 5000
      });
      return true;
   } catch {
      return false;
   }
}

function extractServers(filePath, format) {
   try {
      const raw = fs.readFileSync(filePath, "utf8");
      const config = JSON.parse(raw);
      if (format === "mcpServers") {
         return config.mcpServers || {};
      }
      if (format === "mcp.servers") {
         return (config.mcp && config.mcp.servers) || {};
      }
      return {};
   } catch {
      return {};
   }
}

function checkServer(name, entry) {
   if (entry.disabled === true) {
      return { name, status: "SKIP", reason: "Already disabled", command: entry.command || "" };
   }

   const command = entry.command || "";
   const args = entry.args || [];
   let status = "OK";
   let reason = "";
   const warnings = [];

   // Resolve actual binary (Windows cmd /c <real-binary> pattern)
   let binaryToCheck = command;
   let argsStartIdx = 0;

   if (command === "cmd" && args.length >= 2 && args[0] === "/c") {
      binaryToCheck = args[1];
      argsStartIdx = 2;
   }

   // Check binary exists
   const binResult = checkBinary(binaryToCheck);
   if (!binResult.ok) {
      status = "FAIL";
      reason = path.isAbsolute(binaryToCheck)
         ? "Binary not found: " + binaryToCheck
         : "Command not found in PATH: " + binaryToCheck;
   }

   // Docker-specific: check daemon is running
   if (status === "OK" && binaryToCheck === "docker") {
      if (!checkDocker()) {
         status = "FAIL";
         reason = "Docker daemon not running or not accessible";
      }
   }

   // Check absolute paths in args (skip flags and URLs)
   if (status === "OK") {
      for (let i = argsStartIdx; i < args.length; i++) {
         const arg = args[i];
         if (typeof arg !== "string") continue;
         if (arg.startsWith("-") || arg.startsWith("http")) continue;
         if (path.isAbsolute(arg) && !fs.existsSync(arg)) {
            warnings.push("Arg path not found: " + arg);
         }
      }
      if (warnings.length > 0) {
         status = "WARN";
         reason = warnings.join("; ");
      }
   }

   return { name, status, reason, command: binaryToCheck };
}

// Scan all sources
const results = [];
const sourcesFound = [];

for (const src of ALL_SOURCES) {
   if (!fs.existsSync(src.path)) continue;
   const servers = extractServers(src.path, src.format);
   const names = Object.keys(servers);
   if (names.length === 0) continue;

   sourcesFound.push({ name: src.name, path: src.path, count: names.length });

   for (const [serverName, entry] of Object.entries(servers)) {
      const result = checkServer(serverName, entry);
      result.source = src.name;
      result.configPath = src.path;
      results.push(result);
   }
}

console.log(JSON.stringify({ sources: sourcesFound, servers: results }, null, 2));
'
