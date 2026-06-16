import { useEffect } from 'react';
import { useLocation } from 'react-router-dom';

// Reset scroll to the top of the page on every route change, so navigating
// via the navbar/footer always lands at the top instead of keeping the
// previous page's scroll position.
const ScrollToTop = () => {
    const { pathname } = useLocation();

    useEffect(() => {
        window.scrollTo({ top: 0, left: 0, behavior: 'instant' });
    }, [pathname]);

    return null;
};

export default ScrollToTop;
