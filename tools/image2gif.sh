#!/bin/bash
# image2gif.sh — WSL端实际处理脚本
# 被 image2gif.bat 调用，接收WSL路径参数

set -e

dir="$1"
delay="${2:-0.1}"
fps=$(python3 -c "print(int(1/$delay))" 2>/dev/null || echo 10)

cd "$dir" || { echo "[错误] 无法访问: $dir"; exit 1; }

# 收集图片文件，按文件名排序
shopt -s nullglob
files=(*.png *.jpg *.jpeg *.bmp *.webp *.tiff *.tif)
shopt -u nullglob

if [ ${#files[@]} -eq 0 ]; then
    echo "[错误] 文件夹中没有找到图片文件"
    echo "支持的格式: PNG, JPG, JPEG, BMP, WEBP, TIFF"
    exit 1
fi

echo "找到 ${#files[@]} 张图片，帧间隔 ${delay}秒 (${fps}fps)"
echo ""

# 临时目录存编号后的图片
tmpdir=$(mktemp -d /tmp/img2gif.XXXXXX)
trap "rm -rf '$tmpdir'" EXIT

i=1
for f in "${files[@]}"; do
    printf -v num "%03d" $i
    cp "$f" "$tmpdir/img$num.png"
    ((i++))
done

echo "正在生成 GIF..."

ffmpeg -framerate "$fps" -i "$tmpdir/img%03d.png" \
       -vf "scale=iw:-1:flags=lanczos,split[s0][s1];[s0]palettegen=max_colors=256[p];[s1][p]paletteuse=dither=bayer:bayer_scale=3" \
       -y "$dir/output.gif"

size=$(stat -c%s "$dir/output.gif" 2>/dev/null)
echo ""
echo "[完成] output.gif (${size} 字节)"
