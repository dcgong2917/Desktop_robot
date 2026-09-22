pyinstaller ^
  --onefile ^
  --windowed ^
  --name robot ^
  --add-data "assets;assets" ^
  --hidden-import="rembg" ^
  --hidden-import="onnxruntime" ^
  --hidden-import="bs4" ^
  --hidden-import="zhipuai" ^
  --hidden-import="pymatting" ^
  --copy-metadata="pymatting" ^
  --copy-metadata="rembg" ^
  main.py
