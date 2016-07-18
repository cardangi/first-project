<xsl:stylesheet version="2.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

    <xsl:template match="targets">
        <html>
            <head> 
                <title>
                    <xsl:value-of select="./@title"/>
                </title>
                <link rel="stylesheet" type="text/css">
                    <xsl:attribute name="href">
                        <xsl:value-of select="./@css"/>
                   </xsl:attribute>
                </link>
            </head>
            <body>
                <h2>backup scripts</h2>
                <div class="menu">
                    <ul>
                        <xsl:apply-templates select="workspace" mode="menu"/>
                    </ul>
                </div>
                <xsl:apply-templates select="workspace" mode="detail"/>
            </body>
        </html>
    </xsl:template>

    <xsl:template match="workspace" mode="menu">
        <li>
            <a>
                <xsl:attribute name="href">
                    <xsl:value-of select="concat('#',./@name)"/>
                </xsl:attribute>
                <xsl:value-of select="./@name"/>
            </a>
        </li>
    </xsl:template>

    <xsl:template match="workspace" mode="detail">
        <div>
            <xsl:attribute name="id">
                <xsl:value-of select="./@name"/>
            </xsl:attribute>
            <h3><xsl:value-of select="./@name"/></h3>
            <div class="scripts">
                <table>
                    <tr>
                        <th>ID</th>
                        <th>Name</th>
                        <th>Source</th>
                        <th>Destination</th>
                        <th>Filter</th>
                        <th>Backup</th>
                    </tr>
                    <xsl:apply-templates select="target" mode="detail"/>
                </table>
            </div>
        </div>
    </xsl:template>

    <xsl:template match="target" mode="detail">
        <tr>
        
            <td class="id">
                <xsl:attribute name="id">
                    <xsl:value-of select="./@uid"/>
                </xsl:attribute>
                <xsl:value-of select="./@uid"/>
            </td>
            <td class="name">
                <xsl:value-of select="./@name"/>
            </td>

            <xsl:if test="count(child::source)=1">
                <xsl:apply-templates select="source" mode="mono"/>
            </xsl:if>
            <xsl:if test="count(child::source)>1">
                <td class="source">
                    <xsl:apply-templates select="source" mode="multi"/>
                </td>
            </xsl:if>

            <xsl:apply-templates select="medium"/>

            <xsl:if test="count(child::filter_group/regex_filter)>0">
                <td>
                    <xsl:if test="count(child::filter_group/regex_filter)>1">
                        <xsl:apply-templates select="filter_group/regex_filter" mode="toto"/>
                    </xsl:if>
                    <xsl:if test="count(child::filter_group/regex_filter)=1">
                        <xsl:apply-templates select="filter_group/regex_filter"/>
                    </xsl:if>
                </td>
            </xsl:if>

            <xsl:if test="count(child::lastbackupdate)>0">
                <xsl:apply-templates select="lastbackupdate"/>
            </xsl:if>

        </tr>
    </xsl:template>

    <xsl:template match="source" mode="mono">
        <td class="source">
            <xsl:value-of select="@path"/>
        </td>
    </xsl:template>

    <xsl:template match="source" mode="multi">
        <p>
            <xsl:value-of select="@path"/>
        </p>
    </xsl:template>

    <xsl:template match="medium">
        <td class="destination">
            <xsl:value-of select="@path"/>
        </td>
    </xsl:template>

    <xsl:template match="lastbackupdate">
        <td class="backup">
            <xsl:value-of select="."/>
        </td>
    </xsl:template>

    <xsl:template match="regex_filter">
        <xsl:value-of select="@rgpattern"/>
    </xsl:template>

    <xsl:template match="regex_filter" mode="toto">
        <p>
            <xsl:value-of select="@rgpattern"/>
        </p>
    </xsl:template>

    <xsl:template match="workspace/target[@uid='204959096']" mode="trailer">
        <table>
            <tr>
                <td>
                    <xsl:value-of select="@uid"/>
                </td>
                <td>
                    <xsl:value-of select="./medium/@archive_name"/>
                </td>
            </tr>
        </table>
    </xsl:template>

</xsl:stylesheet>
