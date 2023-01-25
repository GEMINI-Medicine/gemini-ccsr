from distutils.core import setup

with open('README.md', 'r', encoding='utf-8') as f:
    long_description = f.read()

setup(
  name='gemini-ccsr',
  packages=['gemini_ccsr'],
  version='1.0.1',
  license='MIT',
  description='Maps ICD-10 codes to CCSR categories.',
  long_description=long_description,
  long_description_content_type='text/markdown',
  author='Anne Loffler & Daniel Tamming',
  author_email='anne.loffler@unityhealth.to',
  maintainer='GEMINI',
  maintainer_email='gemini.data@unityhealth.to',
  url='https://github.com/GEMINI-Medicine/gemini-ccsr',
  keywords=['ICD', 'ICD10', 'CCSR'],
  python_requires=">=3.8",
  install_requires=[
          'pandas',
          'numpy',
          'tqdm',
      ],
  classifiers=[
    'Development Status :: 3 - Alpha',
    'Intended Audience :: Developers',
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3.8',
    'Programming Language :: Python :: 3.8',
  ],
)
