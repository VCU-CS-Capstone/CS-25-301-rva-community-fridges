import streamlit as st

# Function to add the welcome modal trigger button
def add_welcome_modal_button():
    if st.sidebar.button("Show Welcome Tutorial", key="show_welcome_modal"):
        load_welcome_modal_js()

# Function to load the welcome modal JavaScript
def load_welcome_modal_js():
    st.markdown("""
    <script>
    // Function to create and show modal
    function showWelcomeModal() {
        // Create overlay
        const overlay = document.createElement('div');
        overlay.className = 'modal-overlay';
        
        // Create modal content
        const modal = document.createElement('div');
        modal.className = 'modal-content';
        
        // Add heading
        const heading = document.createElement('h2');
        heading.textContent = '👋 Welcome to the Fridge Monitoring Dashboard!';
        modal.appendChild(heading);
        
        // Add content
        const content = document.createElement('div');
        content.innerHTML = `
            <p>This dashboard provides real-time monitoring of community fridges across Richmond. 
            Here are some quick tips to get started:</p>
            <ul>
                <li>Select a fridge from the sidebar dropdown</li>
                <li>View current temperature and door usage data</li>
                <li>Explore historical data with different time ranges</li>
                <li>Switch to Map View to see all fridges at once</li>
            </ul>
        `;
        modal.appendChild(content);
        
        // Add close button
        const closeBtn = document.createElement('button');
        closeBtn.className = 'modal-close';
        closeBtn.textContent = '✕';
        closeBtn.onclick = function() {
            document.body.removeChild(overlay);
        };
        modal.appendChild(closeBtn);
        
        // Add "Get Started" button
        const startBtn = document.createElement('button');
        startBtn.className = 'modal-button';
        startBtn.textContent = 'Get Started';
        startBtn.onclick = function() {
            document.body.removeChild(overlay);
        };
        modal.appendChild(startBtn);
        
        // Add modal to overlay
        overlay.appendChild(modal);
        
        // Add overlay to body
        document.body.appendChild(overlay);
    }
    
    // Small delay to ensure the page has loaded
    setTimeout(showWelcomeModal, 300);
    </script>
    """, unsafe_allow_html=True)

# Function to automatically show the welcome modal on first visit
def auto_show_welcome_modal():
    st.markdown("""
    <script>
    document.addEventListener('DOMContentLoaded', function() {
        // Function to create and show modal
        function showModal() {
            // Create overlay
            const overlay = document.createElement('div');
            overlay.className = 'modal-overlay';
            
            // Create modal content
            const modal = document.createElement('div');
            modal.className = 'modal-content';
            
            // Add heading
            const heading = document.createElement('h2');
            heading.textContent = '👋 Welcome to the Fridge Monitoring Dashboard!';
            modal.appendChild(heading);
            
            // Add content
            const content = document.createElement('div');
            content.innerHTML = `
                <p>This dashboard provides real-time monitoring of community fridges across Richmond. 
                Here are some quick tips to get started:</p>
                <ul>
                    <li>Select a fridge from the sidebar dropdown</li>
                    <li>View current temperature and door usage data</li>
                    <li>Explore historical data with different time ranges</li>
                    <li>Switch to Map View to see all fridges at once</li>
                </ul>
            `;
            modal.appendChild(content);
            
            // Add close button
            const closeBtn = document.createElement('button');
            closeBtn.className = 'modal-close';
            closeBtn.textContent = '✕';
            closeBtn.onclick = function() {
                document.body.removeChild(overlay);
                // Store in localStorage that the user has seen the welcome message
                localStorage.setItem('welcomeModalSeen', 'true');
            };
            modal.appendChild(closeBtn);
            
            // Add "Get Started" button
            const startBtn = document.createElement('button');
            startBtn.className = 'modal-button';
            startBtn.textContent = 'Get Started';
            startBtn.onclick = function() {
                document.body.removeChild(overlay);
                // Store in localStorage that the user has seen the welcome message
                localStorage.setItem('welcomeModalSeen', 'true');
            };
            modal.appendChild(startBtn);
            
            // Add modal to overlay
            overlay.appendChild(modal);
            
            // Add overlay to body
            document.body.appendChild(overlay);
        }
        
        // Check if user has seen the welcome message before
        if (!localStorage.getItem('welcomeModalSeen')) {
            // Small delay to ensure the page has loaded
            setTimeout(showModal, 500);
        }
    });
    </script>
    """, unsafe_allow_html=True)

# Function to add a tutorial button that triggers a walkthrough
def add_tutorial_button():
    tutorial_trigger = st.sidebar.button("Show Tutorial", key="tutorial_button")
    if tutorial_trigger:
        st.markdown("""
        <script>
        // This would be a tutorial walkthrough implementation
        // In a real implementation, we'd use a proper Streamlit component
        </script>
        """, unsafe_allow_html=True)