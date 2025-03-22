"""Custom timeline component for Streamlit"""
import streamlit.components.v1 as components
import os
import json

def timeline_component(
    milestones,
    height=400
):
    """
    Create an interactive timeline component.
    
    Args:
        milestones: List of milestone objects
        height: Height of the timeline component in pixels
        
    Returns:
        Dictionary containing the dropped milestone data if a milestone was dropped,
        None otherwise
    """
    
    # Calculate sub-component heights
    timeline_height = int(height * 0.4)  # 40% for timeline
    templates_height = int(height * 0.6)  # 60% for templates
    
    # Build the component HTML
    html = f"""
    <div class="timeline-wrapper" style="height: {height}px;">
        <div class="timeline-container" id="timeline" style="height: {timeline_height}px;">
            <div class="timeline-years"></div>
            <div class="timeline-drop-zone" id="timeline-drop-zone">
                Click a milestone below, then click here to place it
            </div>
            <div class="timeline-items" id="timeline-items"></div>
        </div>
        
        <div class="milestone-templates" style="height: {templates_height}px;">
            <div class="milestone-category">
                <h4>Education</h4>
                <div class="milestone-item education" data-type="education" data-name="College">
                    🎓 College Education
                </div>
                <div class="milestone-item education" data-type="education" data-name="Graduate">
                    📚 Graduate School
                </div>
            </div>
            
            <div class="milestone-category">
                <h4>Military</h4>
                <div class="milestone-item military" data-type="military" data-name="Service">
                    🎖️ Military Service
                </div>
                <div class="milestone-item military" data-type="military" data-name="Reserve">
                    🪖 Reserve Duty
                </div>
            </div>
            
            <div class="milestone-category">
                <h4>Work</h4>
                <div class="milestone-item work" data-type="work" data-name="Job">
                    💼 Full-time Job
                </div>
                <div class="milestone-item work" data-type="work" data-name="Internship">
                    💻 Internship
                </div>
            </div>
            
            <div class="milestone-category">
                <h4>Skills</h4>
                <div class="milestone-item skill" data-type="skill" data-name="Training">
                    🛠️ Technical Training
                </div>
                <div class="milestone-item skill" data-type="skill" data-name="Certification">
                    📱 Certification
                </div>
            </div>
        </div>
    </div>
    """
    
    # Add the CSS
    css = """
    <style>
    .timeline-wrapper {
        display: flex;
        flex-direction: column;
        gap: 20px;
        padding: 10px;
        user-select: none;
    }
    
    .timeline-container {
        width: 100%;
        background: #f0f2f6;
        border-radius: 10px;
        padding: 20px;
        position: relative;
        cursor: pointer;
    }
    
    .timeline-years {
        position: absolute;
        bottom: 0;
        left: 0;
        right: 0;
        height: 30px;
    }
    
    .timeline-year {
        position: absolute;
        bottom: 20px;
        width: 2px;
        background: #1f77b4;
        height: 10px;
    }
    
    .timeline-year-label {
        position: absolute;
        bottom: 0;
        transform: translateX(-50%);
        font-size: 12px;
        color: #666;
    }
    
    .timeline-drop-zone {
        position: absolute;
        top: 50%;
        left: 0;
        right: 0;
        height: 60px;
        transform: translateY(-50%);
        background: rgba(255,255,255,0.8);
        border: 2px dashed #ccc;
        border-radius: 5px;
        display: flex;
        align-items: center;
        justify-content: center;
        color: #666;
        transition: all 0.3s;
        cursor: pointer;
    }
    
    .timeline-drop-zone.hover {
        background: rgba(31, 119, 180, 0.1);
        border-color: #1f77b4;
        color: #1f77b4;
    }
    
    .timeline-items {
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 30px;
    }
    
    .milestone-templates {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 20px;
        padding: 10px;
        background: white;
        border-radius: 10px;
        overflow-y: auto;
    }
    
    .milestone-category {
        display: flex;
        flex-direction: column;
        gap: 10px;
    }
    
    .milestone-category h4 {
        margin: 0;
        color: #666;
        text-align: center;
    }
    
    .milestone-item {
        background: white;
        border: 2px solid #1f77b4;
        border-radius: 5px;
        padding: 8px 12px;
        cursor: pointer;
        font-size: 14px;
        transition: all 0.3s;
        text-align: center;
    }
    
    .milestone-item:hover {
        box-shadow: 0 2px 5px rgba(0,0,0,0.2);
        transform: translateY(-1px);
    }
    
    .milestone-item.selected {
        box-shadow: 0 0 0 2px #1f77b4;
        transform: scale(1.05);
    }
    
    .milestone-item.education {
        border-color: #2ecc71;
        background: #eafaf1;
    }
    
    .milestone-item.education.selected {
        box-shadow: 0 0 0 2px #2ecc71;
    }
    
    .milestone-item.military {
        border-color: #e74c3c;
        background: #fdedec;
    }
    
    .milestone-item.military.selected {
        box-shadow: 0 0 0 2px #e74c3c;
    }
    
    .milestone-item.work {
        border-color: #3498db;
        background: #ebf5fb;
    }
    
    .milestone-item.work.selected {
        box-shadow: 0 0 0 2px #3498db;
    }
    
    .milestone-item.skill {
        border-color: #f1c40f;
        background: #fef9e7;
    }
    
    .milestone-item.skill.selected {
        box-shadow: 0 0 0 2px #f1c40f;
    }
    
    .timeline-item {
        position: absolute;
        padding: 8px 12px;
        border-radius: 5px;
        font-size: 14px;
        white-space: nowrap;
    }
    </style>
    """
    
    # Add the JavaScript code
    js = """
    <script>
    // Debug logging function
    function debug(message, data) {
        console.log(`[Timeline] ${message}`, data || '');
    }
    
    // Wait for Streamlit to be ready
    function waitForStreamlit() {
        return new Promise((resolve) => {
            if (window.Streamlit) {
                resolve(window.Streamlit);
            } else {
                const observer = new MutationObserver(() => {
                    if (window.Streamlit) {
                        observer.disconnect();
                        resolve(window.Streamlit);
                    }
                });
                observer.observe(document.body, { childList: true, subtree: true });
            }
        });
    }
    
    // Main initialization function
    async function initialize() {
        debug('Initializing timeline component');
        const Streamlit = await waitForStreamlit();
        debug('Streamlit is ready');
        
        const timeline = document.getElementById('timeline');
        const dropZone = document.getElementById('timeline-drop-zone');
        const itemsContainer = document.getElementById('timeline-items');
        const milestones = document.querySelectorAll('.milestone-item');
        
        let selectedMilestone = null;
        
        function initTimeline() {
            debug('Initializing timeline layout');
            const years = 30;
            const timelineWidth = timeline.offsetWidth - 40;
            const yearWidth = timelineWidth / years;
            
            const yearsContainer = timeline.querySelector('.timeline-years');
            yearsContainer.innerHTML = '';
            
            for (let i = 0; i <= years; i++) {
                const yearMarker = document.createElement('div');
                yearMarker.className = 'timeline-year';
                yearMarker.style.left = `${(i * yearWidth) + 20}px`;
                
                const yearLabel = document.createElement('div');
                yearLabel.className = 'timeline-year-label';
                yearLabel.textContent = `Year ${i}`;
                yearLabel.style.left = `${(i * yearWidth) + 20}px`;
                
                yearsContainer.appendChild(yearMarker);
                yearsContainer.appendChild(yearLabel);
            }
            
            const existingMilestones = MILESTONE_DATA;
            debug('Adding existing milestones', existingMilestones);
            itemsContainer.innerHTML = '';
            existingMilestones.forEach(milestone => {
                addMilestoneToTimeline(milestone);
            });
        }
        
        function addMilestoneToTimeline(milestone) {
            debug('Adding milestone to timeline', milestone);
            const timelineWidth = timeline.offsetWidth - 40;
            const yearWidth = timelineWidth / 30;
            
            const element = document.createElement('div');
            element.className = `timeline-item milestone-item ${milestone.type}`;
            element.textContent = milestone.text;
            element.style.left = `${(milestone.year * yearWidth) + 20}px`;
            element.style.top = '20px';
            
            itemsContainer.appendChild(element);
        }
        
        function getTimelineYear(x) {
            const rect = timeline.getBoundingClientRect();
            const relativeX = x - rect.left - 20;
            const width = rect.width - 40;
            return Math.max(0, Math.min(29, Math.floor((relativeX / width) * 30)));
        }
        
        function updateDropZone(x) {
            if (selectedMilestone) {
                const year = getTimelineYear(x);
                dropZone.setAttribute('data-year', year);
                dropZone.textContent = `Click to place at Year ${year}`;
                dropZone.classList.add('hover');
            } else {
                dropZone.textContent = 'Click a milestone below, then click here to place it';
                dropZone.classList.remove('hover');
            }
        }
        
        // Click handlers for milestones
        milestones.forEach(milestone => {
            milestone.addEventListener('click', () => {
                // Deselect if already selected
                if (selectedMilestone && selectedMilestone.element === milestone) {
                    milestone.classList.remove('selected');
                    selectedMilestone = null;
                    updateDropZone();
                    return;
                }
                
                // Remove selection from previously selected milestone
                if (selectedMilestone) {
                    selectedMilestone.element.classList.remove('selected');
                }
                
                // Select the new milestone
                milestone.classList.add('selected');
                selectedMilestone = {
                    element: milestone,
                    type: milestone.dataset.type,
                    name: milestone.dataset.name,
                    text: milestone.innerText.trim()
                };
                
                updateDropZone();
                debug('Selected milestone', selectedMilestone);
            });
        });
        
        // Timeline click handler
        timeline.addEventListener('click', async (e) => {
            if (!selectedMilestone) return;
            
            const year = getTimelineYear(e.clientX);
            const milestone = {
                type: selectedMilestone.type,
                name: selectedMilestone.name,
                text: selectedMilestone.text,
                year: year
            };
            
            debug('Placed milestone', milestone);
            addMilestoneToTimeline(milestone);
            
            try {
                debug('Sending milestone to Streamlit');
                await Streamlit.setComponentValue(milestone);
                debug('Milestone sent to Streamlit');
            } catch (error) {
                debug('Error sending milestone to Streamlit', error);
            }
            
            // Clear selection
            selectedMilestone.element.classList.remove('selected');
            selectedMilestone = null;
            updateDropZone();
        });
        
        // Timeline hover handler
        timeline.addEventListener('mousemove', (e) => {
            updateDropZone(e.clientX);
        });
        
        timeline.addEventListener('mouseleave', () => {
            if (selectedMilestone) {
                dropZone.textContent = 'Click here to place the selected milestone';
                dropZone.classList.add('hover');
            } else {
                updateDropZone();
            }
        });
        
        // Initialize timeline
        initTimeline();
        window.addEventListener('resize', initTimeline);
        
        // Mark component as ready
        Streamlit.setComponentReady();
        debug('Component initialization complete');
    }
    
    // Start initialization
    debug('Starting component initialization');
    initialize().catch(error => {
        console.error('Timeline initialization error:', error);
    });
    </script>
    """
    
    # Combine everything and create the component
    component_html = f"{css}{html}{js.replace('MILESTONE_DATA', json.dumps(milestones))}"
    
    # Return the component with the correct parameters
    return components.html(
        html=component_html,
        height=height,
        scrolling=True
    ) 