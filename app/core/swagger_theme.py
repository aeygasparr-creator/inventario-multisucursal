HUD_THEME_CSS = """
<style>
  body {
    background: #05080d !important;
  }
  .swagger-ui {
    background: #05080d;
    color: #7fdbff;
    font-family: 'Consolas', 'Courier New', monospace;
  }
  .swagger-ui .topbar {
    background: linear-gradient(90deg, #001a26, #002e40);
    border-bottom: 1px solid #00e5ff;
    box-shadow: 0 0 14px rgba(0, 229, 255, 0.35);
  }
  .swagger-ui .topbar .download-url-wrapper { display: none; }
  .swagger-ui .info .title {
    color: #00e5ff;
    text-shadow: 0 0 8px rgba(0, 229, 255, 0.5);
    font-family: 'Consolas', 'Courier New', monospace;
  }
  .swagger-ui .info .title small.version-stamp {
    background: #00e5ff;
  }
  .swagger-ui .info,
  .swagger-ui .info li,
  .swagger-ui .info p,
  .swagger-ui .info table {
    color: #9fd9e8;
  }
  .swagger-ui .info a { color: #00e5ff; }
  .swagger-ui .scheme-container {
    background: #0a1620;
    box-shadow: none;
    border-bottom: 1px solid #00445580;
  }
  .swagger-ui .opblock-tag {
    color: #00e5ff;
    border-bottom: 1px solid rgba(0, 68, 85, 0.5);
  }
  .swagger-ui .opblock-tag small { color: #5b8a99; }
  .swagger-ui .opblock {
    background: #0a1620;
    border: 1px solid rgba(0, 68, 85, 0.5);
    box-shadow: 0 0 10px rgba(0, 229, 255, 0.08);
    border-radius: 6px;
  }
  .swagger-ui .opblock .opblock-summary-description { color: #7fa8b3; }
  .swagger-ui .opblock.opblock-get {
    border-color: rgba(0, 229, 255, 0.55);
    background: rgba(0, 229, 255, 0.05);
  }
  .swagger-ui .opblock.opblock-post {
    border-color: rgba(57, 255, 136, 0.55);
    background: rgba(57, 255, 136, 0.05);
  }
  .swagger-ui .opblock.opblock-put {
    border-color: rgba(255, 210, 57, 0.55);
    background: rgba(255, 210, 57, 0.05);
  }
  .swagger-ui .opblock.opblock-delete {
    border-color: rgba(255, 77, 77, 0.55);
    background: rgba(255, 77, 77, 0.05);
  }
  .swagger-ui .opblock .opblock-summary-method {
    text-shadow: 0 0 4px currentColor;
    border-radius: 4px;
  }
  .swagger-ui .opblock .opblock-summary-path,
  .swagger-ui .opblock .opblock-summary-operation-id {
    color: #d6f3fb;
  }
  .swagger-ui .btn.authorize {
    background: rgba(0, 229, 255, 0.1);
    border-color: #00e5ff;
    color: #00e5ff;
    box-shadow: 0 0 8px rgba(0, 229, 255, 0.35);
  }
  .swagger-ui .btn.authorize svg { fill: #00e5ff; }
  .swagger-ui .btn.execute {
    background: #00e5ff;
    border-color: #00e5ff;
    color: #05080d;
    font-weight: bold;
    box-shadow: 0 0 12px rgba(0, 229, 255, 0.6);
  }
  .swagger-ui .btn.cancel { border-color: #ff4d4d; color: #ff4d4d; }
  .swagger-ui select,
  .swagger-ui input[type=text],
  .swagger-ui input[type=password],
  .swagger-ui input[type=email],
  .swagger-ui textarea {
    background: #05121a;
    color: #d6f3fb;
    border: 1px solid #00445580;
  }
  .swagger-ui .model-box,
  .swagger-ui .responses-inner,
  .swagger-ui .response-col_description,
  .swagger-ui .tab li {
    background: transparent;
    color: #9fd9e8;
  }
  .swagger-ui table thead tr th,
  .swagger-ui table thead tr td {
    color: #00e5ff;
    border-bottom: 1px solid #00445580;
  }
  .swagger-ui .parameter__name,
  .swagger-ui .parameter__type,
  .swagger-ui .response-col_status {
    color: #9fd9e8;
  }
  .swagger-ui .microlight { background: #05121a !important; color: #d6f3fb; }
  .swagger-ui .highlight-code { background: #05121a; }
  .swagger-ui section.models { border: 1px solid #00445580; background: #0a1620; }
  .swagger-ui section.models .model-container { background: #0a1620; }
  .swagger-ui .model-title { color: #00e5ff; }
  ::-webkit-scrollbar { width: 10px; height: 10px; }
  ::-webkit-scrollbar-track { background: #05080d; }
  ::-webkit-scrollbar-thumb { background: #00445599; border-radius: 4px; }
  .swagger-ui .info .title::after {
    content: " ● SYSTEM ONLINE";
    font-size: 12px;
    color: #39ff88;
    text-shadow: 0 0 6px rgba(57, 255, 136, 0.6);
    vertical-align: middle;
    margin-left: 10px;
  }
</style>
"""
