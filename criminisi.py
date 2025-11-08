from PIL import Image
import numpy as np
import cv2 as cv
import scipy.ndimage as ndimage

#=== ===#
#===SPRAWDŹCIE CZY JEST POPRAWNIE PO MAM DOSYĆ TEGO KODU===#

def criminisi_inpaint(img, mask):
    img_np = np.array(img)
    target = (np.array(mask) > 0).astype(np.uint8)
    confidence = (1 - target).astype(np.float32)
    h, w, _ = img_np.shape
    patch_size = 9
    r = patch_size // 2
    alpha = 255.0
    #===Limit iteracji dla bezpieczeństwa===#
    max_iterations = 500
    iteration = 0
    #===Normalne===#
    target_float = target.astype(np.float32)
    nx = ndimage.sobel(target_float, axis=1)
    ny = ndimage.sobel(target_float, axis=0)
    norm = np.sqrt(nx**2 + ny**2 + 1e-6)
    nx /= norm
    ny /= norm
    #===GRADIENTY===#
    gray = np.mean(img_np, axis=2).astype(np.float32)
    gx = ndimage.sobel(gray, axis=1)
    gy = ndimage.sobel(gray, axis=0)
    while np.any(target) and iteration < max_iterations:
        iteration += 1
        #===SZUKANIE FRONTU===#
        kernel = np.ones((3, 3), np.uint8)
        dilated = cv.dilate(target, kernel, iterations=1)
        front_mask = (dilated - target) > 0
        front = np.argwhere(front_mask & (target == 0))
        if len(front) == 0:
            #===BRAK FRONTU, UZYJ PIKSELI===#
            front = np.argwhere(target > 0)
            if len(front) == 0:
                break
            #===MAŁA PRÓBKA===#
            if len(front) > 100:
                indices = np.random.choice(len(front), 100, replace=False)
                front = front[indices]
        
        if len(front) > 50:
            step = len(front) // 50
            front = front[::max(1, step)]
        #===PRIORYTETY===#
        priorities = []
        valid_front = []
        for y, x in front:
            y_slice = slice(max(0, y-r), min(h, y+r+1))
            x_slice = slice(max(0, x-r), min(w, x+r+1))
            patch_conf = confidence[y_slice, x_slice]
            c = np.mean(patch_conf)
            patch_target = target[y_slice, x_slice]
            known_mask = 1 - patch_target
            if np.sum(known_mask) == 0:
                continue
            grad_mag = np.sqrt(gx[y_slice, x_slice]**2 + gy[y_slice, x_slice]**2)
            grad_mag_masked = grad_mag * known_mask
            if np.max(grad_mag_masked) > 0:
                max_idx = np.unravel_index(np.argmax(grad_mag_masked), grad_mag_masked.shape)
                gy_loc = y - r + max_idx[0]
                gx_loc = x - r + max_idx[1]
                if 0 <= gy_loc < h and 0 <= gx_loc < w:
                    max_gy = gy[gy_loc, gx_loc]
                    max_gx = gx[gy_loc, gx_loc]
                    max_mag = np.sqrt(max_gx**2 + max_gy**2) + 1e-6
                    isophote_y = -max_gx / max_mag
                    isophote_x = max_gy / max_mag
                    n_p_y, n_p_x = ny[y, x], nx[y, x]
                    dot = abs(isophote_x * n_p_y + isophote_y * n_p_x)
                    d = dot / alpha
                else:
                    d = 0.1
            else:
                d = 0.1
            p_val = c * d + 0.001 #===0.001, LEPIEJ DZIAŁA===#
            priorities.append(p_val)
            valid_front.append((y, x))
        if not valid_front:
            break
        #===WYBÓR PUNKTU O NAJWYŻSZYM PRIORYTECIE===#
        best_idx = np.argmax(priorities)
        y, x = valid_front[best_idx]
        c_hat = confidence[y, x]
        patch_p = img_np[max(0, y-r):min(h, y+r+1), max(0, x-r):min(w, x+r+1)]
        mask_p = target[max(0, y-r):min(h, y+r+1), max(0, x-r):min(w, x+r+1)]
        best_ssd = np.inf
        best_q = None
        #===OGRANICZENIE OBSZARU POSZUKIWAŃ===#
        search_radius = min(100, max(h, w) // 4)
        y_min = max(r, y - search_radius)
        y_max = min(h - r - 1, y + search_radius)
        x_min = max(r, x - search_radius)
        x_max = min(w - r - 1, x + search_radius)
        step = max(1, search_radius // 50)
        for qy in range(y_min, y_max, step):
            for qx in range(x_min, x_max, step):
                #===CZY ZNAMY PATCH===#
                patch_target = target[qy-r:qy+r+1, qx-r:qx+r+1]
                if np.any(patch_target):
                    continue
                #===OBLICZENIE SSD===#
                patch_q = img_np[qy-r:qy+r+1, qx-r:qx+r+1]
                #===TE SAME ROZMIARY PATCHÓW===#
                min_h = min(patch_p.shape[0], patch_q.shape[0])
                min_w = min(patch_p.shape[1], patch_q.shape[1])
                if min_h < patch_size // 2 or min_w < patch_size // 2:
                    continue
                patch_p_crop = patch_p[:min_h, :min_w]
                patch_q_crop = patch_q[:min_h, :min_w]
                mask_p_crop = mask_p[:min_h, :min_w]
                known_mask = 1 - mask_p_crop
                if np.sum(known_mask) == 0:
                    continue
                #===OBLICZENIE SSD===#
                diff = (patch_p_crop.astype(np.float32) - patch_q_crop.astype(np.float32)) * known_mask[:, :, np.newaxis]
                ssd = np.sum(diff**2) / (np.sum(known_mask) + 1e-6)
                if ssd < best_ssd:
                    best_ssd = ssd
                    best_q = (qy, qx)
        if best_q is None:
            #=== TZW. FALLBACK DLA NAPLIŻESZGO PATCHA===#
            for radius in [10, 20, 50]:
                y_min = max(r, y - radius)
                y_max = min(h - r - 1, y + radius)
                x_min = max(r, x - radius)
                x_max = min(w - r - 1, x + radius)
                for qy in range(y_min, y_max, max(1, radius // 10)):
                    for qx in range(x_min, x_max, max(1, radius // 10)):
                        patch_target = target[qy-r:qy+r+1, qx-r:qx+r+1]
                        if not np.any(patch_target):
                            best_q = (qy, qx)
                            break
                    if best_q:
                        break
                if best_q:
                    break
            if best_q is None:
                break
        #===WYPEŁNIENIE PATCHEM===#
        qy, qx = best_q
        for dy in range(-r, r+1):
            for dx in range(-r, r+1):
                ny_, nx_ = y + dy, x + dx
                nqy, nqx = qy + dy, qx + dx
                if (0 <= ny_ < h and 0 <= nx_ < w and
                    0 <= nqy < h and 0 <= nqx < w and
                    target[ny_, nx_]):
                    img_np[ny_, nx_] = img_np[nqy, nqx]
                    target[ny_, nx_] = 0
                    confidence[ny_, nx_] = c_hat
        #=== AKTUALIZACJA GRADIENTÓW===#
        if iteration % 10 == 0:
            gray = np.mean(img_np, axis=2).astype(np.float32)
            gx = ndimage.sobel(gray, axis=1)
            gy = ndimage.sobel(gray, axis=0)
    return Image.fromarray(img_np)
