# A MultiLingual Summarizer for Enhanced Text Comprehension

## Overview

This project is a multi-lingual summarizer application built using Python and Streamlit. It allows users to upload various types of documents (PDF, Excel, PPT, DOC, TXT), provide YouTube video links, or enter website URLs and sample text. The application extracts text from these sources, processes it, and provides summaries and answers to user queries in multiple languages.

## Features

- **Multi-lingual Support:** Summarize text in 40 different languages.
- **Document Upload:** Supports PDF, Excel, PPT, DOC, and TXT files.
- **YouTube Integration:** Extracts and summarizes transcripts from YouTube videos.
- **Website Integration:** Extracts and summarizes content from websites.
- **Sample Text:** Allows users to input and summarize custom text.
- **Conversational Q&A:** Provides answers to user queries based on the extracted content.

## Installation

1. Clone the repository:
    ```sh
    git clone https://github.com/prabhas6567/multilingual-summarizer.git
    cd multilingual-summarizer
    ```

2. Create and activate a virtual environment:
    ```sh
    python -m venv venv
    source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
    ```

3. Install the required dependencies:
    ```sh
    pip install -r requirements.txt
    ```

4. Set up the environment variables:
    - Create a file named [api.env](http://_vscodecontentref_/0) in the project root directory.
    - Add your Google API key to the [api.env](http://_vscodecontentref_/1) file:
        ```plaintext
        GOOGLE_API_KEY="your-google-api-key"
        ```

## Usage

1. Run the Streamlit application:
    ```sh
    streamlit run app.py
    ```

2. Open your web browser and navigate to `http://localhost:8501`.

3. Use the sidebar to select the file type, language, and summary length.

4. Upload your files, enter YouTube links, website URLs, or sample text.

5. Click "Submit & Process" to extract and process the content.

6. Ask questions based on the processed content and receive answers.

## File Structure

- [app.py](http://_vscodecontentref_/2): Main application file containing the Streamlit interface and core logic.
- [api.env](http://_vscodecontentref_/3): Environment variables file containing the Google API key.
- [requirements.txt](http://_vscodecontentref_/4): List of required Python packages.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License.