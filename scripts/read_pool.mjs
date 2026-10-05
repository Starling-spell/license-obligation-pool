import {createClient} from 'genlayer-js';
import {studionet} from 'genlayer-js/chains';
import dns from 'node:dns';
dns.setDefaultResultOrder('ipv4first');
const [address, account, pool, ...slots] = process.argv.slice(2);
if (!/^0x[0-9a-fA-F]{40}$/.test(address ?? '') || !/^0x[0-9a-fA-F]{40}$/.test(account ?? '')) throw Error('Contract and principal addresses required');
const client = createClient({chain: studionet});
async function read(functionName, args) {
  for (let attempt = 0; attempt < 3; attempt++) {
    try { return await client.readContract({address, functionName, args}); }
    catch (error) { if (attempt === 2) throw error; }
  }
}
const result = {pool: await read('get_pool', [account, pool]), entries: {}};
if (process.env.LICENSE_POOL_EXPECTED) {
  const expected = JSON.parse(process.env.LICENSE_POOL_EXPECTED);
  for (const [key, value] of Object.entries(expected)) {
    if (JSON.stringify(result.pool[key]) !== JSON.stringify(value)) throw Error(`Pool assertion failed: ${key}`);
  }
  result.assertions = 'PASSED';
}
for (const slot of slots) {
  const entry = await read('get_entry', [account, pool, slot]);
  result.entries[slot] = {active: entry.active, status: entry.report.status, vector: entry.report.vector,
    reason: entry.report.reason, hash_match: entry.report.hash_match, root: entry.report.root,
    observed_hash: entry.report.observed_hash};
}
console.log(JSON.stringify(result));
