import React from 'react';
import {
  GitIcon,
  ConfluenceIcon,
  NotionIcon,
  JiraIcon,
} from '@/components/icons';
import { Badge } from '@/components/ui/badge';
import {
  FileText,
  FilePlus,
  FileEdit as LucideFileEdit,
  Save,
  TerminalIcon,
  FolderIcon,
  FileIcon,
  LinkIcon,
  Loader2,
  ListChecks,
} from 'lucide-react';

interface FetchServicesToolProps {
  toolInvocation: any;
  state: string;
  index: string;
}

export const FetchServicesTool: React.FC<FetchServicesToolProps> = ({
  toolInvocation,
  state,
  index,
}) => {
  const args = 'args' in toolInvocation ? toolInvocation.args : undefined;
  const result =
    state === 'result' && 'result' in toolInvocation
      ? toolInvocation.result
      : undefined;
  const toolName: string = toolInvocation?.toolName || '';

  const getGitRepoInfo = (gitUrl: string) => {
    const match = gitUrl?.match(/github\.com[:/]([^/]+)\/([^/.]+)/);
    if (match) return `${match[1]}/${match[2]}`;
    const parts = (gitUrl || '').split('/');
    const lastPart = parts[parts.length - 1] || '';
    return lastPart.replace('.git', '') || 'repository';
  };

  // Compute UI configuration per tool using a switch-case
  let title = 'Service';
  let contentText = '';
  const statusReady = 'Ready';
  let statusWorking = 'Working...';
  let statusDone = 'Done';
  let icon: React.ReactNode = null;
  let titleTooltip: string | undefined = undefined;

  switch (toolName) {
    case 'web_search':
    case 'web_fetch': {
      title = 'Web Search';
      icon = <LinkIcon className='h-4 w-4 text-gray-600 dark:text-gray-400' />;
      const url: string = args?.url || '';
      const searchTerm: string = args?.prompt || args?.search_term || '';
      const getDomain = (input: string) => {
        try {
          const domain = new URL(input).hostname;
          return domain.replace('www.', '');
        } catch {
          return input || searchTerm || 'web search';
        }
      };
      contentText = url ? getDomain(url) : searchTerm || 'web search';
      titleTooltip = url || searchTerm;
      statusWorking = 'Loading...';
      statusDone = 'Fetched';
      break;
    }
    case 'git_clone': {
      title = 'Git Clone';
      icon = <GitIcon className='h-4 w-4 text-gray-600 dark:text-gray-400' />;
      const url: string = args?.url || '';
      contentText = getGitRepoInfo(url);
      titleTooltip = url;
      statusWorking = 'Cloning...';
      statusDone = 'Cloned';
      break;
    }
    case 'mcp__atlassian__getConfluencePage': {
      title = 'Fetch Confluence Page';
      icon = (
        <ConfluenceIcon className='h-4 w-4 text-gray-600 dark:text-gray-400' />
      );

      if (state === 'result' && result) {
        try {
          // Handle the result which might be wrapped in an array
          let pageData = result;

          // If result is a string, parse it
          if (typeof result === 'string') {
            pageData = JSON.parse(result);
          }

          // If result is an array (from the toolInvocation.result format), get the first item
          if (Array.isArray(pageData) && pageData.length > 0) {
            const firstItem = pageData[0];
            if (
              firstItem &&
              typeof firstItem === 'object' &&
              'text' in firstItem
            ) {
              pageData = JSON.parse(firstItem.text);
            }
          }

          // Extract the page title - Confluence has it directly as 'title'
          const pageTitle = pageData?.title || 'Untitled';
          const spaceId = pageData?.spaceId || '';

          contentText = pageTitle;
          titleTooltip = `${pageTitle} (Space: ${spaceId}, ID: ${pageData?.id || args?.pageId})`;
        } catch (error) {
          console.error('Error parsing Confluence page data:', error);
          contentText = 'Confluence Page';
          titleTooltip = args?.pageId || '';
        }
      } else {
        // While loading
        contentText = args?.pageId
          ? `Loading ${args.pageId}...`
          : 'Loading page...';
        titleTooltip = args?.pageId || '';
      }

      statusWorking = 'Fetching page...';
      statusDone = 'Page loaded';
      break;
    }

    case 'mcp__atlassian__getJiraIssue': {
      title = 'Fetch Jira Issue';
      icon = <JiraIcon className='h-4 w-4 text-gray-600 dark:text-gray-400' />;

      if (state === 'result' && result) {
        try {
          // Handle the result which might be wrapped in an array
          let issueData = result;

          // If result is a string, parse it
          if (typeof result === 'string') {
            issueData = JSON.parse(result);
          }

          // If result is an array (from the toolInvocation.result format), get the first item
          if (Array.isArray(issueData) && issueData.length > 0) {
            const firstItem = issueData[0];
            if (
              firstItem &&
              typeof firstItem === 'object' &&
              'text' in firstItem
            ) {
              issueData = JSON.parse(firstItem.text);
            }
          }

          // Extract the issue key and summary
          const issueKey = issueData?.key || '';
          const summary = issueData?.fields?.summary || 'Untitled';
          const issueType = issueData?.fields?.issuetype?.name || 'Issue';
          const status = issueData?.fields?.status?.name || '';

          contentText = `${issueKey}: ${summary}`;
          titleTooltip = `${issueKey} - ${summary} (${issueType}, Status: ${status})`;
        } catch (error) {
          console.error('Error parsing Jira issue data:', error);
          contentText = 'Jira Issue';
          titleTooltip = args?.issueIdOrKey || '';
        }
      } else {
        // While loading
        contentText = args?.issueIdOrKey
          ? `Loading ${args.issueIdOrKey}...`
          : 'Loading issue...';
        titleTooltip = args?.issueIdOrKey || '';
      }

      statusWorking = 'Fetching issue...';
      statusDone = 'Issue loaded';
      break;
    }

    case 'mcp__atlassian__createJiraIssue': {
      title = 'Create Jira Issue';
      icon = <JiraIcon className='h-4 w-4 text-gray-600 dark:text-gray-400' />;

      if (state === 'result' && result) {
        try {
          // Handle the result which might be wrapped in an array
          let issueData = result;

          // If result is a string, parse it
          if (typeof result === 'string') {
            issueData = JSON.parse(result);
          }

          // If result is an array (from the toolInvocation.result format), get the first item
          if (Array.isArray(issueData) && issueData.length > 0) {
            const firstItem = issueData[0];
            if (
              firstItem &&
              typeof firstItem === 'object' &&
              'text' in firstItem
            ) {
              issueData = JSON.parse(firstItem.text);
            }
          }

          // Extract the issue key and summary from args
          const issueKey = issueData?.key || '';
          const summary = args?.summary || 'New Issue';
          const projectKey = args?.projectKey || '';
          const issueType = args?.issueTypeName || 'Issue';

          contentText = `${issueKey}: ${summary}`;
          titleTooltip = `Created ${issueType} in ${projectKey} - ${summary}`;
        } catch (error) {
          console.error('Error parsing created Jira issue data:', error);
          contentText = 'New Jira Issue';
          titleTooltip = args?.summary || 'Creating issue...';
        }
      } else {
        // While creating
        contentText = args?.summary
          ? `Creating: ${args.summary}...`
          : 'Creating issue...';
        titleTooltip = args?.summary || 'Creating new issue';
      }

      statusWorking = 'Creating issue...';
      statusDone = 'Issue created';
      break;
    }

    case 'mcp__notion__API-retrieve-a-page': {
      title = 'Fetch Notion Page';
      icon = (
        <NotionIcon className='h-4 w-4 text-gray-600 dark:text-gray-400' />
      );

      if (state === 'result' && result) {
        try {
          // Handle the result which might be wrapped in an array
          let pageData = result;

          // If result is a string, parse it
          if (typeof result === 'string') {
            pageData = JSON.parse(result);
          }

          // If result is an array (from the toolInvocation.result format), get the first item
          if (Array.isArray(pageData) && pageData.length > 0) {
            const firstItem = pageData[0];
            if (
              firstItem &&
              typeof firstItem === 'object' &&
              'text' in firstItem
            ) {
              pageData = JSON.parse(firstItem.text);
            }
          }

          // Extract the page title
          const pageTitle =
            pageData?.properties?.title?.title?.[0]?.plain_text || 'Untitled';
          const emoji = pageData?.icon?.emoji || '';

          // Combine emoji and title
          contentText = emoji ? `${emoji} ${pageTitle}` : pageTitle;
          titleTooltip = pageData?.url || `Page ID: ${args?.page_id}`;
        } catch (error) {
          console.error('Error parsing Notion page data:', error);
          contentText = 'Notion Page';
          titleTooltip = args?.page_id || '';
        }
      } else {
        // While loading
        contentText = args?.page_id
          ? `Loading ${args.page_id}...`
          : 'Loading page...';
        titleTooltip = args?.page_id || '';
      }

      statusWorking = 'Fetching page...';
      statusDone = 'Page loaded';
      break;
    }
    case 'text': {
      title = 'Assistant Message';
      icon = <FileText className='h-4 w-4 text-gray-600 dark:text-gray-400' />;
      const text = args?.text || '';
      // Truncate long text for display
      contentText = text.length > 60 ? text.substring(0, 60) + '...' : text;
      titleTooltip = text;
      statusWorking = 'Processing...';
      statusDone = 'Completed';
      break;
    }
    case 'execute_command': {
      title = 'Terminal';
      icon = <TerminalIcon size={16} color='#11054C' />;
      const command: string = args?.command || '';
      const description: string | undefined = args?.description;
      contentText = command;
      titleTooltip = description ? `${command} - ${description}` : command;
      statusWorking = 'Running...';
      statusDone = 'Completed';
      break;
    }
    case 'glob_files': {
      title = 'Glob Search';
      icon = <FileIcon size={16} color='#11054C' />;
      const pattern: string = args?.pattern || '';
      const path: string = args?.path || './';
      contentText = `${pattern} in ${path}`;
      titleTooltip = `${pattern} in ${path}`;
      // If result is present, count files
      if (state === 'result') {
        const files = result
          ? String(result)
              .split('\n')
              .filter((f: string) => f.trim())
          : [];
        statusDone = files.length > 0 ? `${files.length} found` : 'No matches';
      } else {
        statusDone = 'Done';
      }
      statusWorking = 'Searching...';
      break;
    }
    case 'search_files':
    case 'search_file': {
      title = 'Search Files';
      icon = <FileIcon size={16} color='#11054C' />;
      const pattern: string = args?.pattern || '';
      const path: string = args?.path || '';
      contentText = pattern ? `${pattern} in ${path}` : path;
      titleTooltip = contentText;
      if (state === 'result') {
        const lines = String(result || '')
          .split('\n')
          .filter((line: string) => line.trim());
        statusDone = lines.length > 0 ? `${lines.length} found` : 'No matches';
      }
      statusWorking = 'Searching...';
      break;
    }
    case 'write_file':
    case 'read_file':
    case 'create_file': {
      const op = toolName;
      const filePath: string =
        args?.file_path || args?.target_file || args?.path || 'Untitled';
      const filename = (filePath.split('/') as string[]).pop() || 'file';
      contentText = filename;
      titleTooltip = filename;
      if (op === 'read_file') {
        title = 'Read File';
        icon = <FileText size={16} color='#11054C' />;
        statusWorking = 'Reading...';
        statusDone = 'Read';
      } else if (op === 'create_file') {
        title = 'Create File';
        icon = <FilePlus size={16} color='#11054C' />;
        statusWorking = 'Creating...';
        statusDone = 'Created';
      } else {
        title = 'Write File';
        icon = <Save size={16} color='#11054C' />;
        statusWorking = 'Writing...';
        statusDone = 'Saved';
      }
      break;
    }
    case 'edit_file': {
      const filePath: string =
        args?.file_path || args?.target_file || args?.path || 'Untitled';
      const filename = (filePath.split('/') as string[]).pop() || 'file';
      title = 'Edit File';
      icon = <LucideFileEdit size={16} color='#11054C' />;
      contentText = filename;
      titleTooltip = filename;
      statusWorking = 'Editing...';
      statusDone = 'Edited';
      break;
    }
    case 'list_directory': {
      title = 'List Directory';
      icon = <FolderIcon size={16} color='#11054C' />;
      const path: string = args?.path || './';
      contentText = path;
      titleTooltip = path;
      if (state === 'result') {
        const folderMatches = (String(result || '').match(/([\w-]+\/)/g) || [])
          .length;
        const fileMatches = (
          String(result || '').match(/([\w.-]+\.[a-zA-Z0-9]+)/g) || []
        ).length;
        const itemCount = folderMatches + fileMatches;
        statusDone = itemCount > 0 ? `${itemCount} items` : 'Listed';
      }
      statusWorking = 'Listing...';
      break;
    }
    case 'task_manager': {
      title = 'Task Manager';
      icon = <ListChecks size={16} color='#11054C' />;
      const description: string = args?.description || 'Processing task';
      const subagentType: string = args?.subagent_type || '';

      contentText = description;
      titleTooltip = `${description} (${subagentType})`;

      statusWorking = 'Processing task...';
      statusDone = 'Task completed';

      // If we have a result, try to extract completion summary
      if (state === 'result' && result) {
        try {
          const resultText =
            typeof result === 'string' ? result : JSON.stringify(result);

          // Check for various completion patterns
          if (resultText.includes('successfully')) {
            statusDone = 'Completed successfully';
          } else if (resultText.includes('complete')) {
            statusDone = 'Task completed';
          } else if (resultText.includes('generated')) {
            // Extract what was generated if mentioned
            const generatedMatch = resultText.match(/generated\s+(\d+\s+\w+)/i);
            if (generatedMatch) {
              statusDone = `Generated ${generatedMatch[1]}`;
            } else {
              statusDone = 'Generation completed';
            }
          } else if (resultText.includes('processed')) {
            statusDone = 'Processing completed';
          }
        } catch {
          // Keep default status
        }
      }
      break;
    }
    default: {
      // Fallback for future tools: show generic info
      title = toolName
        .replace(/_/g, ' ')
        .replace(/\b\w/g, c => c.toUpperCase());
      icon = <Loader2 size={16} color='#11054C' />;
      const summary: string = args?.summary || '';
      contentText = summary || 'Invoked';
      statusWorking = 'Working...';
      statusDone = 'Done';
    }
  }

  const statusText =
    state === 'result'
      ? statusDone
      : state === 'call'
        ? statusWorking
        : statusReady;

  return (
    <div key={index} className='mb-2'>
      <div className='rounded-lg bg-gray-50 p-3'>
        {/* Header: icon + title on left, status badge on right */}
        <div className='mb-1.5 flex items-center justify-between border-b border-gray-200 pb-2'>
          <div className='flex items-center gap-2'>
            {icon}
            <span className='text-sm font-medium text-gray-700 dark:text-gray-300'>
              {title}
            </span>
          </div>
          <Badge variant='default' className='text-xs'>
            {statusText}
          </Badge>
        </div>

        {/* Content: concise descriptor with ellipsis */}
        <div>
          <code
            className='block truncate rounded font-mono text-xs text-gray-600'
            title={titleTooltip}
          >
            {contentText}
          </code>
        </div>
      </div>
    </div>
  );
};
