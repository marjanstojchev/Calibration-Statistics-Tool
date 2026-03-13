"""
Applies targeted improvements to parsePTU2data.py:
1. Fix file-open logic (os.path.isfile check + correct try/except)
2. Translate German error strings to English
3. Guard buildArrays() with try/except
4. Guard myLogger in FileTitle.parseFileTitle
"""
import re

with open('shared/parsePTU2data.py', 'r') as f:
    src = f.read()

# ── 1. Fix the file-open block inside interpretData ─────────────────────────
# Find the block: "    # Try to read the file" through (and including) the
# `else:` clause's `for line in content:` line (still inside the else: body).
# We replace the try/except/else with a cleaner version that:
#   - adds an os.path.isfile guard
#   - splits into two separate except clauses
#   - moves content reading outside any else: clause (no bug)
old_open_block = """\
    # Try to read the file
    try:
        f = io.open(fileNamePath, encoding='utf-8')
    except (IOError, UnicodeDecodeError) as err:
        try:
            f = io.open(fileNamePath, encoding='windows-1252')
        except IOError as ioErr:
            # errorString='try reading: ' +fileNamePath+ ' Exception = ' + str(ioErr)
            errorString = strMeasName + ' File does not exist! Insert a valid file path.'
            ptu2ParseData.errorList.append(errorString)
    else:
        # Read the lines of the file and remove all white spaces
        with f:
            content = f.readlines()
        content = [line.strip() for line in content]

        # Traverse through every line of the content
        for line in content:"""

new_open_block = """\
    # Try to read the file
    if not os.path.isfile(fileNamePath):
        ptu2ParseData.errorList.append(strMeasName + ' File does not exist: ' + fileNamePath)
        return
    f = None
    try:
        f = io.open(fileNamePath, encoding='utf-8')
    except UnicodeDecodeError:
        try:
            f = io.open(fileNamePath, encoding='windows-1252')
        except (IOError, OSError) as err:
            ptu2ParseData.errorList.append(strMeasName + ' Could not read file: ' + str(err))
            return
    except (IOError, OSError) as err:
        ptu2ParseData.errorList.append(strMeasName + ' Could not open file: ' + str(err))
        return
    with f:
        content = f.readlines()
    content = [line.strip() for line in content]

    # Traverse through every line of the content
    for line in content:"""

assert old_open_block in src, "Could not find old open block"
src = src.replace(old_open_block, new_open_block, 1)

# The `for line in content:` loop body and the "Setup error list" block were
# inside the else: clause (8-space indent).  After the replacement above they
# are now at the function body level, so we must dedent them by 4 spaces.
# Find the new `    for line in content:` line and dedent its body (everything
# up to the closing `# Parses the antenna info part` comment).
lines = src.splitlines(keepends=True)

for_idx = next(
    i for i, l in enumerate(lines)
    if l == '    for line in content:\n'
)
end_idx = next(
    i for i, l in enumerate(lines)
    if i > for_idx and (l.startswith('# ') or l.startswith('def '))
)

fixed = lines[:for_idx + 1]
for line in lines[for_idx + 1:end_idx]:
    if line.startswith('        ') and line.strip():
        fixed.append(line[4:])   # dedent 4 spaces
    else:
        fixed.append(line)
fixed += lines[end_idx:]
src = ''.join(fixed)

# ── 2. Translate German error strings ───────────────────────────────────────
src = src.replace(
    "' Error 1 - Antennendaten einlesen'",
    "' Error reading antenna data'"
)
src = src.replace(
    "' Error 2 - Chirp ' + str(chirpcounter) + ' daten einlesen'",
    "' Error reading chirp ' + str(chirpcounter) + ' data'"
)
src = src.replace(
    "' Error 3 - Messdaten einlesen'",
    "' Error reading measurement data'"
)

# ── 3. Guard buildArrays() with try/except ───────────────────────────────────
src = src.replace(
    """\
    if len(ptu2ParseData.errorList) == 0:
        ptu2ParseData.bDataValid = True
        ptu2ParseData.buildArrays()
    else:
        ptu2ParseData.bDataValid = False""",
    """\
    if len(ptu2ParseData.errorList) == 0:
        try:
            ptu2ParseData.bDataValid = True
            ptu2ParseData.buildArrays()
        except Exception as err:
            ptu2ParseData.bDataValid = False
            ptu2ParseData.errorList.append(fileNamePath + ' Error building data arrays: ' + str(err))
    else:
        ptu2ParseData.bDataValid = False"""
)

# ── 4. Guard myLogger in FileTitle.parseFileTitle ───────────────────────────
src = src.replace(
    "                    myLogger.error('Empty sensor muster list!')",
    "                    if myLogger:\n                        myLogger.error('Empty sensor muster list!')"
)

with open('shared/parsePTU2data.py', 'w') as f:
    f.write(src)

print("Done.")
