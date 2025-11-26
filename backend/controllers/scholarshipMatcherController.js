const path = require('path');
const { spawn } = require('child_process');

const PREDICT_SCRIPT_PATH = path.join(
  __dirname,
  '..',
  'scholarship_loan_matcher_ml',
  'prediction',
  'predict.py'
);
const PYTHON_BIN = process.env.PYTHON_BIN || 'python';

function runPredictor(profile, topN = 5) {
  return new Promise((resolve, reject) => {
    const profileArg = JSON.stringify(profile || {});
    const args = [PREDICT_SCRIPT_PATH, '--profile', profileArg, '--top_n', String(topN)];
    const child = spawn(PYTHON_BIN, args, { stdio: ['ignore', 'pipe', 'pipe'] });

    let stdout = '';
    let stderr = '';

    child.stdout.on('data', (chunk) => {
      stdout += chunk.toString();
    });

    child.stderr.on('data', (chunk) => {
      stderr += chunk.toString();
    });

    child.on('close', (code) => {
      if (code !== 0) {
        return reject(new Error(stderr || `Predictor exited with code ${code}`));
      }
      try {
        const parsed = JSON.parse(stdout);
        resolve(parsed.results || []);
      } catch (err) {
        reject(new Error(`Failed to parse predictor output: ${err.message}`));
      }
    });
  });
}

exports.matchScholarships = async (req, res) => {
  try {
    const profile = req.body || {};
    const topN = Number(req.query.topN) || 5;

    if (!Object.keys(profile).length) {
      return res.status(400).json({ message: 'Student profile payload is required.' });
    }

    const matches = await runPredictor(profile, topN);
    return res.json({ matches, count: matches.length });
  } catch (error) {
    console.error('Scholarship matcher error:', error);
    return res.status(500).json({
      message: 'Unable to fetch scholarship matches at this time.',
      error: error.message,
    });
  }
};


