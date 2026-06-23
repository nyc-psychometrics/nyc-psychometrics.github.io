// get the ninja-keys element
const ninja = document.querySelector('ninja-keys');

// add the home and posts menu items
ninja.data = [{
    id: "nav-home",
    title: "home",
    section: "Navigation",
    handler: () => {
      window.location.href = "/";
    },
  },{id: "nav-programs",
          title: "programs",
          description: "Doctoral programs in psychometrics, measurement, and quantitative methods across New York City.",
          section: "Navigation",
          handler: () => {
            window.location.href = "/programs/";
          },
        },{id: "nav-events",
          title: "events",
          description: "",
          section: "Navigation",
          handler: () => {
            window.location.href = "/events/";
          },
        },{id: "nav-join",
          title: "join",
          description: "Join the NYC Psychometrics Google Group to get announcements and connect with the community.",
          section: "Navigation",
          handler: () => {
            window.location.href = "/join/";
          },
        },{id: "post-google-gemini-updates-flash-1-5-gemma-2-and-project-astra",
        
          title: 'Google Gemini updates: Flash 1.5, Gemma 2 and Project Astra <svg width="1.2rem" height="1.2rem" top=".5rem" viewBox="0 0 40 40" xmlns="http://www.w3.org/2000/svg"><path d="M17 13.5v6H5v-12h6m3-3h6v6m0-6-9 9" class="icon_svg-stroke" stroke="#999" stroke-width="1.5" fill="none" fill-rule="evenodd" stroke-linecap="round" stroke-linejoin="round"></path></svg>',
        
        description: "We’re sharing updates across our Gemini family of models and a glimpse of Project Astra, our vision for the future of AI assistants.",
        section: "Posts",
        handler: () => {
          
            window.open("https://blog.google/technology/ai/google-gemini-update-flash-ai-assistant-io-2024/", "_blank");
          
        },
      },{id: "post-displaying-external-posts-on-your-al-folio-blog",
        
          title: 'Displaying External Posts on Your al-folio Blog <svg width="1.2rem" height="1.2rem" top=".5rem" viewBox="0 0 40 40" xmlns="http://www.w3.org/2000/svg"><path d="M17 13.5v6H5v-12h6m3-3h6v6m0-6-9 9" class="icon_svg-stroke" stroke="#999" stroke-width="1.5" fill="none" fill-rule="evenodd" stroke-linecap="round" stroke-linejoin="round"></path></svg>',
        
        description: "",
        section: "Posts",
        handler: () => {
          
            window.open("https://medium.com/@al-folio/displaying-external-posts-on-your-al-folio-blog-b60a1d241a0a?source=rss-17feae71c3c4------2", "_blank");
          
        },
      },{id: "news-welcome-the-nyc-psychometrics-group-website-is-up-join-our-google-group-to-hear-about-upcoming-events-tada",
          title: 'Welcome! The NYC Psychometrics Group website is up. Join our Google Group to...',
          description: "",
          section: "News",},{id: "news-modern-modeling-methods-m3-conference",
          title: 'Modern Modeling Methods (M3) Conference',
          description: "",
          section: "News",handler: () => {
              window.location.href = "/news/announcement_2/";
            },},{id: "news-nyc-psychometrics-event-ben-domingue",
          title: 'NYC Psychometrics Event: Ben Domingue',
          description: "",
          section: "News",handler: () => {
              window.location.href = "/news/announcement_3/";
            },},{id: "projects-cuny-graduate-center",
          title: 'CUNY Graduate Center',
          description: "Ph.D. in Educational Psychology",
          section: "Projects",handler: () => {
              window.location.href = "/projects/1_program/";
            },},{id: "projects-new-york-university",
          title: 'New York University',
          description: "Ph.D. in Statistics and Computational Social Science",
          section: "Projects",handler: () => {
              window.location.href = "/projects/2_program/";
            },},{id: "projects-fordham-university",
          title: 'Fordham University',
          description: "Ph.D. in Psychometrics and Quantitative Psychology",
          section: "Projects",handler: () => {
              window.location.href = "/projects/3_program/";
            },},{id: "projects-teachers-college-columbia-university",
          title: 'Teachers College, Columbia University',
          description: "Doctoral program in Measurement, Evaluation, and Statistics",
          section: "Projects",handler: () => {
              window.location.href = "/projects/4_program/";
            },},{
        id: 'social-email',
        title: 'email',
        section: 'Socials',
        handler: () => {
          window.open("mailto:%70%73%79%63%68%6F%6D%65%74%72%69%63%73-%6E%79%63@%67%6F%6F%67%6C%65%67%72%6F%75%70%73.%63%6F%6D", "_blank");
        },
      },{
        id: 'social-rss',
        title: 'RSS Feed',
        section: 'Socials',
        handler: () => {
          window.open("/feed.xml", "_blank");
        },
      },{
      id: 'light-theme',
      title: 'Change theme to light',
      description: 'Change the theme of the site to Light',
      section: 'Theme',
      handler: () => {
        setThemeSetting("light");
      },
    },
    {
      id: 'dark-theme',
      title: 'Change theme to dark',
      description: 'Change the theme of the site to Dark',
      section: 'Theme',
      handler: () => {
        setThemeSetting("dark");
      },
    },
    {
      id: 'system-theme',
      title: 'Use system default theme',
      description: 'Change the theme of the site to System Default',
      section: 'Theme',
      handler: () => {
        setThemeSetting("system");
      },
    },];
