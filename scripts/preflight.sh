#!/usr/bin/env bash
# Read only inventory. Does not install packages, change services, or print secrets.
set -u
printf '\nCampusCompass Nano preflight\n'
printf '\nHost and project\n'
hostname
pwd
printf '\nArchitecture\n'
uname -m
printf '\nOperating system\n'
if [ -r /etc/os-release ]; then cat /etc/os-release; fi
printf '\nMemory\n'
free -h
printf '\nProject filesystem space\n'
df -h .
printf '\nGPU\n'
if command -v nvidia-smi >/dev/null 2>&1; then nvidia-smi; else printf 'nvidia-smi not found\n'; fi
printf '\nCUDA compiler\n'
if command -v nvcc >/dev/null 2>&1; then nvcc --version; else printf 'nvcc not on PATH; inspect the existing toolkit before installing anything\n'; fi
printf '\nAvailable development tools\n'
for tool in git python3 uv node npm cmake gcc docker codex; do
  if command -v "$tool" >/dev/null 2>&1; then
    command -v "$tool"
    "$tool" --version 2>&1 | head -n 2
  else
    printf '%s: not on PATH\n' "$tool"
  fi
done
printf '\nListening local ports\n'
if command -v ss >/dev/null 2>&1; then ss -ltn; fi
printf '\nPreflight complete. No system configuration was changed.\n'
