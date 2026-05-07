<?php
// Shared DB + helpers. Required by save_lead.php / save_profile.php.

declare(strict_types=1);

function load_config(): array {
    // Look for config in safe locations, in order of preference.
    // 1. Explicit env override (for testing or non-standard layouts)
    // 2. ABOVE public_html (production best practice — not web-accessible)
    // 3. Same dir as _db.php (dev fallback only)
    $candidates = array_filter([
        getenv('SIGNAL_CONFIG') ?: null,
        __DIR__ . '/../../../signal_config.php',  // ~/public_html/signal/orbit/_db.php → ~/signal_config.php
        __DIR__ . '/../../signal_config.php',     // alternative depth
        __DIR__ . '/config.php',                  // dev fallback (gitignored)
    ]);
    foreach ($candidates as $path) {
        if (is_file($path)) {
            return require $path;
        }
    }
    http_response_code(500);
    error_log('SIGNAL: no config found. Looked in: ' . implode(', ', $candidates));
    echo json_encode(['error' => 'server_misconfigured']);
    exit;
}

function db_connect(array $cfg): PDO {
    $dsn = "mysql:host={$cfg['db']['host']};dbname={$cfg['db']['name']};charset={$cfg['db']['charset']}";
    try {
        return new PDO($dsn, $cfg['db']['user'], $cfg['db']['pass'], [
            PDO::ATTR_ERRMODE            => PDO::ERRMODE_EXCEPTION,
            PDO::ATTR_DEFAULT_FETCH_MODE => PDO::FETCH_ASSOC,
            PDO::ATTR_EMULATE_PREPARES   => false,
        ]);
    } catch (PDOException $e) {
        http_response_code(503);
        error_log('SIGNAL: DB connect failed: ' . $e->getMessage());
        echo json_encode(['error' => 'db_unavailable']);
        exit;
    }
}

function send_json_cors(array $cors_origins): void {
    $origin = $_SERVER['HTTP_ORIGIN'] ?? '';
    if (in_array($origin, $cors_origins, true)) {
        header("Access-Control-Allow-Origin: $origin");
        header('Access-Control-Allow-Methods: POST, OPTIONS');
        header('Access-Control-Allow-Headers: Content-Type');
    }
    header('Content-Type: application/json; charset=utf-8');
    if (($_SERVER['REQUEST_METHOD'] ?? '') === 'OPTIONS') {
        http_response_code(204);
        exit;
    }
}

function read_json_body(): array {
    $raw = file_get_contents('php://input');
    if ($raw === false || $raw === '') {
        http_response_code(400);
        echo json_encode(['error' => 'empty_body']);
        exit;
    }
    $data = json_decode($raw, true);
    if (!is_array($data)) {
        http_response_code(400);
        echo json_encode(['error' => 'invalid_json']);
        exit;
    }
    return $data;
}

function client_ip_hash(): string {
    $ip = $_SERVER['HTTP_X_FORWARDED_FOR']
        ?? $_SERVER['HTTP_CF_CONNECTING_IP']
        ?? $_SERVER['REMOTE_ADDR']
        ?? '0.0.0.0';
    if (str_contains($ip, ',')) {
        $ip = trim(explode(',', $ip)[0]);
    }
    return hash('sha256', $ip . '|signal-salt-2026');
}

function rate_limit_check(PDO $pdo, string $table, string $ipHash, string $email, array $limits): void {
    // Per-IP per hour
    $stmt = $pdo->prepare("SELECT COUNT(*) FROM $table WHERE ip_hash = ? AND created_at > NOW() - INTERVAL 1 HOUR");
    $stmt->execute([$ipHash]);
    if ((int)$stmt->fetchColumn() >= $limits['per_ip_per_hour']) {
        http_response_code(429);
        echo json_encode(['error' => 'too_many_requests']);
        exit;
    }
    // Per-email per day
    $stmt = $pdo->prepare("SELECT COUNT(*) FROM $table WHERE email = ? AND created_at > NOW() - INTERVAL 1 DAY");
    $stmt->execute([$email]);
    if ((int)$stmt->fetchColumn() >= $limits['per_email_per_day']) {
        http_response_code(429);
        echo json_encode(['error' => 'too_many_requests']);
        exit;
    }
}

function clean_str(?string $s, int $maxLen = 500): string {
    if ($s === null) return '';
    $s = trim($s);
    // Strip CR/LF (header injection defense)
    $s = str_replace(["\r", "\n"], ' ', $s);
    return mb_substr($s, 0, $maxLen);
}

function valid_email(string $e): bool {
    return (bool) filter_var($e, FILTER_VALIDATE_EMAIL);
}

function notify_telegram(array $cfg, string $text): void {
    if (empty($cfg['telegram']['bot_token']) || empty($cfg['telegram']['chat_id'])) return;
    $url = "https://api.telegram.org/bot{$cfg['telegram']['bot_token']}/sendMessage";
    $payload = http_build_query([
        'chat_id'    => $cfg['telegram']['chat_id'],
        'text'       => $text,
        'parse_mode' => 'HTML',
        'disable_web_page_preview' => true,
    ]);
    $ch = curl_init($url);
    curl_setopt_array($ch, [
        CURLOPT_RETURNTRANSFER => true,
        CURLOPT_POST           => true,
        CURLOPT_POSTFIELDS     => $payload,
        CURLOPT_TIMEOUT        => 4,
    ]);
    $resp = curl_exec($ch);
    $code = curl_getinfo($ch, CURLINFO_HTTP_CODE);
    curl_close($ch);
    if ($code !== 200) {
        error_log("SIGNAL: telegram notify failed (HTTP $code): " . substr((string)$resp, 0, 300));
    }
}

function html_escape(string $s): string {
    return htmlspecialchars($s, ENT_QUOTES | ENT_HTML5, 'UTF-8');
}
