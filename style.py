import streamlit as st

def apply_styles():
    """
    Applies custom CSS styles to the Streamlit application
    with support for both light and dark themes, using
    !important to override default Streamlit styles.
    """
    st.markdown("""
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;600&display=swap');
            
            html, body, [class*="st-"] {
                font-family: 'Poppins', sans-serif;
            }

            /* --- Light Theme Styles (Default) --- */
            .stApp {
                background-color: #f0f2f6;
            }

            .stApp > header {
                background-color: #ffffff;
                border-bottom: 1px solid #e0e0e0;
            }

            h1 {
                color: #1a1a1a;
                font-weight: 600;
                text-align: center;
                padding-bottom: 20px;
            }
            
            .stTextInput>div>div>input {
                border-radius: 10px;
                border: 1px solid #ccc;
                padding: 8px;
                transition: border-color 0.3s;
            }
            
            .stTextInput>div>div>input:focus {
                border-color: #00f2fe;
                box-shadow: 0 0 5px rgba(0, 242, 254, 0.5);
                outline: none;
            }

            .stTabs [data-baseweb="tab-list"] button {
                background-color: #ffffff;
                border-radius: 10px 10px 0 0;
            }
            
            /* --- Dark Theme Overrides --- */
            @media (prefers-color-scheme: dark) {
                .stApp {
                    background-color: #1a1a1a !important;
                }
                
                .stApp > header {
                    background-color: #262626 !important;
                    border-bottom: 1px solid #363636 !important;
                }
                
                h1 {
                    color: #f0f2f6 !important;
                }
                
                .stTextInput>div>div>input {
                    background-color: #262626 !important;
                    border: 1px solid #444 !important;
                    color: #f0f2f6 !important;
                }
                
                .stTextInput>div>div>input:focus {
                    border-color: #00f2fe !important;
                    box-shadow: 0 0 5px rgba(0, 242, 254, 0.5) !important;
                }

                .stDataFrame {
                    background-color: #262626 !important;
                }

                .stTabs [data-baseweb="tab-list"] button {
                    background-color: #262626 !important;
                    color: #f0f2f6 !important;
                }
            }
            
            /* --- Common Styles (apply to both themes) --- */
            .stButton>button {
                width: 100%;
                background-image: linear-gradient(to right, #4facfe 0%, #00f2fe 100%);
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 25px;
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
                transition: all 0.3s ease;
            }
            
            .stButton>button:hover {
                box-shadow: 0 6px 8px rgba(0, 0, 0, 0.15);
                transform: translateY(-2px);
            }
            
            .stDataFrame {
                border-radius: 10px;
                overflow: hidden;
                box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
            }
            
            /* Target only the header text in st.expander */
            .stApp [data-testid="stExpander"] div[role="button"] p {
                margin: 0 !important;
                flex-grow: 1 !important;
                overflow: hidden !important;
                white-space: nowrap !important;
                text-overflow: ellipsis !important;
                min-width: 0 !important;
            }
            /* Explicitly make sure the arrow/icon is excluded */
            .stApp [data-testid="stExpander"] div[role="button"] svg,
            .stApp [data-testid="stExpander"] div[role="button"] [data-testid="stExpanderIconContainer"] {
                flex-shrink: 0 !important;
                min-width: 24px;   /* Adjust as needed */
                margin-left: 8px;  /* Space between text and icon */
            }

            /* Dark mode overrides for expander */
            @media (prefers-color-scheme: dark) {
                .stApp [data-testid="stExpander"] {
                    background-color: #262626 !important;
                }
                .stApp [data-testid="stExpander"] div[role="button"] {
                    background-color: #333 !important;
                    color: #f0f2f6 !important;
                }
            }
        </style>
    """, unsafe_allow_html=True)






