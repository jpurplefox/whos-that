import { UserMenu } from './UserMenu';
import { LanguageSwitcher } from './LanguageSwitcher';
import styles from './HeaderBar.module.css';

export function HeaderBar() {
  return (
    <div className={styles.headerBar}>
      <UserMenu />
      <div className={styles.separator} />
      <LanguageSwitcher />
    </div>
  );
}
