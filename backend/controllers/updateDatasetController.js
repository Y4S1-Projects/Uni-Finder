const path = require('path');
const { spawn } = require('child_process');

const PYTHON_BIN = process.env.PYTHON_BIN || 'python';
const UPDATE_PIPELINE_PATH = path.join(
  __dirname,
  '..',
  'scholarship_loan_matcher_ml',
  'pipeline',
  'update_pipeline.py'
);

function runUpdatePipeline() {
  return new Promise((resolve, reject) => {
    // Run the pipeline as a one-off script printing JSON to stdout
    const code = [
      'import json, traceback',
      'from scholarship_loan_matcher_ml.pipeline.update_pipeline import run_full_update',
      'try:',
      '    summary = run_full_update()',
      '    print(json.dumps({"success": True, "summary": summary}))',
      'except Exception as exc:',
      '    err = {"success": False, "error": str(exc), "details": traceback.format_exc()}',
      '    print(json.dumps(err))',
    ].join('; ');

    const child = spawn(PYTHON_BIN, ['-c', code], {
      cwd: path.join(__dirname, '..'),
      stdio: ['ignore', 'pipe', 'pipe'],
    });

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
        return reject(new Error(stderr || `Update pipeline exited with code ${code}`));
      }
      try {
        const parsed = JSON.parse(stdout || '{}');
        resolve(parsed);
      } catch (err) {
        reject(new Error(`Failed to parse pipeline output: ${err.message}`));
      }
    });
  });
}

exports.triggerUpdate = async (req, res) => {
  try {
    const result = await runUpdatePipeline();
    if (!result.success) {
      return res.status(500).json({
        success: false,
        error: result.error || 'Dataset update failed.',
        details: result.details || null,
      });
    }

    const updatedAt =
      (result.summary && result.summary.finished_at) || new Date().toISOString();

    return res.json({
      success: true,
      updated_at: updatedAt,
      summary: result.summary || {},
    });
  } catch (error) {
    console.error('Dataset update error:', error);
    return res.status(500).json({
      success: false,
      error: error.message,
      details: error.stack,
    });
  }
};




