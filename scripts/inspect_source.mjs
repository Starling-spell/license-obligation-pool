import crypto from 'node:crypto';
import dns from 'node:dns';
dns.setDefaultResultOrder('ipv4first');
const revision = '31ba1a50e5397e00a304dbadc76531740e89ee48';
for (const license of process.argv.slice(2)) {
  if (!['MIT', 'BSD-2-Clause', 'BSD-3-Clause', 'Apache-2.0', 'ISC'].includes(license)) throw Error('Unsupported license');
  const url = `https://raw.githubusercontent.com/spdx/license-list-data/${revision}/text/${license}.txt`;
  let body;
  for (let attempt = 0; attempt < 3; attempt++) {
    try {
      const response = await fetch(url, {signal: AbortSignal.timeout(30000)});
      if (!response.ok) throw Error(`HTTP ${response.status}`);
      body = Buffer.from(await response.arrayBuffer());
      break;
    } catch (error) { if (attempt === 2) throw error; }
  }
  console.log(JSON.stringify({license, url, bytes: body.length, sha256: crypto.createHash('sha256').update(body).digest('hex')}));
}
