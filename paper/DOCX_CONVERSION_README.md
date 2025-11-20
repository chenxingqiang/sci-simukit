# LaTeX to DOCX Conversion Guide

## ✅ Conversion Complete

The paper has been successfully converted from LaTeX to DOCX format.

**Output file**: `strain_doped_graphullerene.docx` (19 KB)

---

## 📄 What's Included

### ✅ Successfully Converted
- **Full text content**: All sections, paragraphs, and content
- **Mathematical equations**: Converted to MathML format
- **Tables**: Table structure and data preserved
- **Section numbering**: Automatic section numbering maintained
- **Title and authors**: Document metadata included

### ⚠️ Manual Adjustments Needed

1. **Figures** (2 images)
   - `figures/publication_quality/figure2_band_structure.pdf`
   - `figures/publication_quality/figure3_mobility_strain.pdf`
   - **Action**: Insert manually from `paper/figures/publication_quality/` folder

2. **Bibliography**
   - References are cited as `~\cite{...}` in the text
   - **Action**: Need to process separately or add manually
   - Bibliography file: `strain_graphullerene_50refs.bib`

3. **Formatting**
   - Some LaTeX-specific formatting may need adjustment
   - Check equation formatting in Word
   - Adjust table borders and styling if needed

---

## 🔧 How to Improve the DOCX

### Add Figures
1. Open `strain_doped_graphullerene.docx` in Microsoft Word
2. Find placeholders: "figure2_band_structure" and "figure3_mobility_strain"
3. Insert → Picture → Select from `figures/publication_quality/` folder
4. Add captions using Word's caption feature

### Process Bibliography

**Option 1: Manual (Quick)**
```bash
# View the .bib file
cat strain_graphullerene_50refs.bib

# Copy references to the end of DOCX manually
```

**Option 2: Use Zotero/Mendeley**
- Import `strain_graphullerene_50refs.bib` into reference manager
- Use Word plugin to insert citations and generate bibliography

**Option 3: Reconvert with Bibliography**
```bash
cd /Users/xingqiangchen/sci-simukit/paper

# Requires pandoc-citeproc
pandoc strain_doped_graphullerene.tex \
  --bibliography=strain_graphullerene_50refs.bib \
  --citeproc \
  --number-sections \
  --standalone \
  --mathml \
  -o strain_doped_graphullerene_with_refs.docx
```

---

## 📊 Conversion Command Used

```bash
pandoc strain_doped_graphullerene.tex \
  --number-sections \
  --standalone \
  --mathml \
  -o strain_doped_graphullerene.docx
```

### Parameters Explained
- `--number-sections`: Automatic section numbering
- `--standalone`: Complete document (not fragment)
- `--mathml`: Convert LaTeX math to MathML (Word compatible)
- `-o`: Output file name

---

## 🔄 Alternative Conversion Methods

### Method 1: pandoc with full features
```bash
pandoc strain_doped_graphullerene.tex \
  --bibliography=strain_graphullerene_50refs.bib \
  --citeproc \
  --number-sections \
  --standalone \
  --mathml \
  --reference-doc=custom_template.docx \
  -o output.docx
```

### Method 2: latex2rtf (alternative tool)
```bash
# If latex2rtf is installed
latex2rtf strain_doped_graphullerene.tex
# Then open .rtf in Word and save as .docx
```

### Method 3: LaTeX → PDF → Word
```bash
# Compile to PDF first
pdflatex strain_doped_graphullerene.tex
bibtex strain_doped_graphullerene
pdflatex strain_doped_graphullerene.tex
pdflatex strain_doped_graphullerene.tex

# Then use Adobe Acrobat or online converter to convert PDF to DOCX
```

---

## 📝 Post-Conversion Checklist

- [ ] Open DOCX in Microsoft Word
- [ ] Check all equations render correctly
- [ ] Insert Figure 2 (band structure)
- [ ] Insert Figure 3 (mobility vs strain)
- [ ] Add figure captions
- [ ] Check Table 1 formatting
- [ ] Process bibliography/references
- [ ] Verify section numbering
- [ ] Check formatting of:
  - [ ] Title
  - [ ] Author names and affiliations
  - [ ] Abstract
  - [ ] Keywords
  - [ ] Acknowledgments
- [ ] Final proofread

---

## 💡 Tips for Best Results

### Equation Formatting
- Word displays MathML equations natively
- If equations look strange, right-click → Convert to Professional format
- For complex equations, you may need to adjust spacing manually

### Table Formatting
- Add borders: Select table → Design → Borders
- Adjust column widths for better appearance
- Center-align numeric data

### Figure Quality
- Use high-resolution figures (300 dpi or higher)
- Save figures as PNG or high-quality JPG for Word
- Consider using original PDF figures for print quality

---

## 🆘 Troubleshooting

### Equations Not Displaying
**Solution**: Ensure Word has MathML support (Word 2016+)
- Alternative: Convert equations to images in LaTeX first

### Figures Missing
**Solution**: Figures must be in the same relative path or inserted manually
- Copy `figures/` folder to same directory as DOCX

### Bibliography Not Included
**Solution**: Use `--citeproc` flag with pandoc or add manually
- Requires proper .bib file format

### Chinese Characters Not Displaying
**Solution**: Ensure Word has proper font support
- Change font to one supporting Chinese (e.g., SimSun, Microsoft YaHei)

---

## 📧 Additional Help

For complex conversions or journal-specific formatting:
1. Check journal's submission guidelines for Word templates
2. Consider using Overleaf's "Download as Word" feature if available
3. Use professional conversion services for final submission

---

## 📊 File Information

**Source**: `strain_doped_graphullerene.tex` (232 lines)  
**Output**: `strain_doped_graphullerene.docx` (19 KB)  
**Conversion Tool**: Pandoc 3.6.3  
**Date**: November 20, 2025  

---

**✅ Conversion successful! The DOCX file is ready for further editing in Microsoft Word.**

*For questions about the conversion, refer to the pandoc documentation: https://pandoc.org/MANUAL.html*

