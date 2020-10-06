mkdir -p ~/.streamlit/

echo "\
[general]\n\
email = \"pau.vilar.ribo@gmail.com\"\n\
" > ~/.streamlit/credentials.toml

echo "\
[server]\n\
headless = true\n\
enableCORS=false\n\
port = $PORT\n\